from datetime import datetime,timedelta
from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from consts.cnario_consts import Constants as KruizasterConsts
from kruizaster import utils as Utils
from kruizaster import cnarios as CnarioHandler
from kruizaster.settings import KruizasterSettings
from starlette.websockets import WebSocket, WebSocketDisconnect
import threading
import json

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/assets", StaticFiles(directory="assets"), name="static")

exp_data = {}
data_lock = threading.Lock()


# Function to indent json as in the UI it's single lined to see a JSON
def json_indent(data, indent=4):
    return json.dumps(data, indent=indent)


# Adding filter to templates
templates.env.filters["json_indent"] = json_indent


def process_create_exp_update_results(experiment_name: str,
                                      num_days: int,
                                      start_time: datetime,
                                      scenario: str,
                                      total_duration_in_mins: int,
                                      interval_time: int,
                                      interval_unit: str,
                                      total_entries: int,
                                      interval_time_in_mins: int):

    # Check if experiment name is not None
    if experiment_name is not None or experiment_name != "":

        # Create Experiment
        Utils.create_kruize_experiment(experiment_name, interval_time_in_mins)

        # Create a gate to check of experiment exists (so that we won't lock for creation process)
        is_exists = True

        # Aquire lock
        with data_lock:
            if experiment_name not in exp_data:
                is_exists = False

        # Create a minified entry list to iterate over the list to generate results
        entry_min_list = []
        # Proceed if experiment not exists
        if not is_exists:

            # init the day to 1
            day = 1
            # Go back in time with Iron Man's Quantum GPS :P
            real_start_time = start_time - timedelta(minutes=total_duration_in_mins)
            # Set Start time to the past calculated time
            entry_start_time = real_start_time
            # init day entry to 0 (We increment in loop don't worry it starts with 1)
            day_entry_id = 0
            # Loop over the entries
            for entry_id in range(1, total_entries + 1):
                # Check if we crossed the day
                if entry_id * interval_time_in_mins > day * 24 * 60:
                    # Increase day count
                    day = day + 1
                    # Reset Day Entry
                    day_entry_id = 0
                # As I told you we increment :P
                day_entry_id = day_entry_id + 1
                # Travel a bit forward in time and calculate end time (Consumes some PYM Particles :D)
                entry_end_time = entry_start_time + timedelta(minutes=interval_time_in_mins)
                # Convert start time to string -> To have less drama when we are accessing from dict or for matching
                start_time_string = Utils.format_date_to_standard_string(entry_start_time)
                # Convert end time as well to string (Don't ask why! jus do it!)
                end_time_string = Utils.format_date_to_standard_string(entry_end_time)
                # Add these minified details to list
                entry_min_list.append({
                    KruizasterConsts.ENTRY_ID: entry_id,
                    KruizasterConsts.DAY: day,
                    KruizasterConsts.DAY_ENTRY_ID: day_entry_id,
                    KruizasterConsts.INTERVAL_START_TIME: start_time_string,
                    KruizasterConsts.INTERVAL_END_TIME:end_time_string
                })
                # The future has become present (It's jus we are progressing to next iteration)
                entry_start_time = entry_end_time

            # Create a template for experiment schema to store in dict
            exp_data_content = {
                KruizasterConsts.METADATA: {
                    KruizasterConsts.STATUS: KruizasterConsts.CREATING,
                    KruizasterConsts.TOTAL_DURATION: total_duration_in_mins,
                    KruizasterConsts.MEASUREMENT_DURATION: interval_time_in_mins,
                    KruizasterConsts.TOTAL_ENTRIES: total_entries,
                    KruizasterConsts.CURRENT_ENTRY: 1,
                    KruizasterConsts.COMPLETED_ENTRIES: 0,
                    KruizasterConsts.ENTRY_MIN_LIST: entry_min_list,
                    KruizasterConsts.RECOMMENDATIONS_GENERATED: 0,
                    KruizasterConsts.UPDATE_RESULTS_SUCCESS: 0,
                    KruizasterConsts.UPDATE_RESULTS_FAILED: 0
                },
                KruizasterConsts.KRUIZASTER_EXP_DATA: {
                    KruizasterConsts.KRUIZASTER_EXP_RESULTS: {
                        # Results will be stored here
                    },
                    KruizasterConsts.KRUIZASTER_EXP_RECS: {
                        # Recommendations will be stored here
                    }
                }
            }
            # Aquire lock and push the template and tag to the experiment name
            with data_lock:
                exp_data[experiment_name] = exp_data_content
        # Itrerate over the list to generate payload
        for entry in entry_min_list:
            # Set the values appropriately
            day                 = entry[KruizasterConsts.DAY]
            entry_id            = entry[KruizasterConsts.ENTRY_ID]
            day_entry_id        = entry[KruizasterConsts.DAY_ENTRY_ID]
            start_time_string   = entry[KruizasterConsts.INTERVAL_START_TIME]
            end_time_string     =  entry[KruizasterConsts.INTERVAL_END_TIME]
            # Init a list instance to store all metric content
            metric_data_list = []
            # Loop over available metrics
            for metric in KruizasterConsts.ALL_METRICS:
                # Get results based on scenario
                metric_data = CnarioHandler.get_results_of_scenario(scenario, metric)
                # Check if not none and append to list
                if metric_data is not None:
                    metric_data_list.append(metric_data)
            # Create results template to load to kruize
            update_results_template = {
                KruizasterConsts.VERSION: "1.0",
                KruizasterConsts.EXPERIMENT_NAME: experiment_name,
                KruizasterConsts.INTERVAL_START_TIME: start_time_string,
                KruizasterConsts.INTERVAL_END_TIME: end_time_string,
                KruizasterConsts.KUBERNETES_OBJECTS: [
                    {
                        KruizasterConsts.TYPE: KruizasterConsts.DEPLOYMENT,
                        KruizasterConsts.NAME: KruizasterConsts.SAMPLE_DEPLOYMENT,
                        KruizasterConsts.NAMESPACE: KruizasterConsts.DEFAULT,
                        KruizasterConsts.CONTAINERS: [
                            {
                                KruizasterConsts.CONTAINER_IMAGE_NAME: KruizasterConsts.SAMPLE_IMAGE,
                                KruizasterConsts.CONTAINER_NAME: KruizasterConsts.SAMPLE_CONTAINER,
                                KruizasterConsts.METRICS: metric_data_list
                            }
                        ]
                    }
                ]
            }
            result_content = {
                KruizasterConsts.METADATA: {
                    KruizasterConsts.ENTRY_ID: entry_id,
                    KruizasterConsts.DAY: day,
                    KruizasterConsts.DAY_ENTRY_ID: day_entry_id
                },
                KruizasterConsts.DATA: update_results_template
            }
            with data_lock:
                exp_data[experiment_name][KruizasterConsts.KRUIZASTER_EXP_DATA][KruizasterConsts.KRUIZASTER_EXP_RESULTS][start_time_string] = result_content
            Utils.update_kruize_results(update_results_template)


@app.get(KruizasterConsts.ServiceInfo.Kruizaster.ServicePaths.ROOT)
async def home(request: Request):
    exp_name = Utils.get_random_exp_name()
    with data_lock:
        while exp_name in exp_data:
            exp_name = Utils.get_random_exp_name()

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "scenarios": KruizasterConsts.SCENARIOS,
            "experiment_name": exp_name,
            "interval_duration_opts": KruizasterConsts.INTERVAL_DURATION_OPTS,
            "create_disaster_path": KruizasterConsts.ServiceInfo.Kruizaster.ServicePaths.CREATE_DISASTER
        }
    )


@app.get(KruizasterConsts.ServiceInfo.Kruizaster.ServicePaths.TEST)
async def test(request: Request):
    return { "Current Kruize Setting ": KruizasterSettings.KRUIZE_BASE_URL}


@app.websocket(KruizasterConsts.ServiceInfo.Kruizaster.ServicePaths.UPDATES_SOCKET)
async def updates_endpoint(websocket: WebSocket):
    await websocket.accept()



@app.post(KruizasterConsts.ServiceInfo.Kruizaster.ServicePaths.CREATE_DISASTER)
async def generate_jsons(request: Request,
                         experiment_name: str = Form(...),
                         num_days: int = Form(...),
                         start_time: datetime = Form(...),
                         scenario: str = Form(...),
                         interval_duration: str = Form(...)):
    experiment_name = experiment_name.strip()
    interval_duration = interval_duration.strip()
    total_duration_in_mins = num_days * 24 * 60
    total_entries = 0
    interval_time = 0
    interval_unit = ""
    interval_time_in_mins = 0
    if interval_duration in KruizasterConsts.INTERVAL_DURATION_OPTS:
        splited_val = interval_duration.split(" ")
        interval_time = int(splited_val[0])
        interval_unit = splited_val[1].lower()
        if interval_unit in KruizasterConsts.INTERVAL_DURATION_UNITS:
            if interval_unit == KruizasterConsts.MINUTES:
                interval_time_in_mins = interval_time
            elif interval_unit == KruizasterConsts.HOURS:
                interval_time_in_mins = interval_time * 60
        total_entries = int(total_duration_in_mins / interval_time_in_mins)

    process_create_exp_update_results(experiment_name=experiment_name,
                                      num_days=num_days,
                                      start_time=start_time,
                                      scenario=scenario.strip(),
                                      total_duration_in_mins=total_duration_in_mins,
                                      interval_time=interval_time,
                                      interval_unit=interval_unit,
                                      total_entries=total_entries,
                                      interval_time_in_mins=interval_time_in_mins)


    return {}
