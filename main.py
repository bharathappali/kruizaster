import time
from datetime import datetime,timedelta
from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from consts.cnario_consts import Constants as KruizasterConsts
from kruizaster import utils as Utils
from kruizaster import cnarios as CnarioHandler
from kruizaster.settings import KruizasterSettings
from starlette.websockets import WebSocket, WebSocketDisconnect
import asyncio
import threading
import json
import uvicorn
import signal

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/assets", StaticFiles(directory="assets"), name="static")


# Lock for exp_data
data_lock = threading.Lock()
# Lock for connection_map
socket_lock = threading.Lock()

# Use data_lock when ever you access this data structure
exp_data = {}

# Use socket_lock when ever you access this data structure
connection_map = {}

# Function to indent json as in the UI it's single lined to see a JSON
def json_indent(data, indent=4):
    return json.dumps(data, indent=indent)


# Adding filter to templates
templates.env.filters["json_indent"] = json_indent


async def process_create_exp_update_results(websocket: WebSocket, experiment_name: str, scenario: str):
    entry_min_list = []
    # init the recommendation counter
    rec_counter = 0
    with data_lock:
        entry_min_list = exp_data[experiment_name][KruizasterConsts.METADATA][KruizasterConsts.ENTRY_MIN_LIST]
    # Iterate over the list to generate payload
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
        # Create the update result content in a much better verbose structure and add it to the results list
        result_content = {
            KruizasterConsts.METADATA: {
                KruizasterConsts.ENTRY_ID: entry_id,
                KruizasterConsts.DAY: day,
                KruizasterConsts.DAY_ENTRY_ID: day_entry_id
            },
            KruizasterConsts.DATA: update_results_template
        }
        # Acquire the lock to write data to the structure
        with data_lock:
            exp_data[experiment_name][KruizasterConsts.KRUIZASTER_EXP_DATA][KruizasterConsts.KRUIZASTER_EXP_RESULTS][end_time_string] = result_content
        # Proceed to update kruize results
        update_results_response_code = Utils.update_kruize_results(results=update_results_template,
                                                                   exp_name=experiment_name,
                                                                   interval_end_time=end_time_string,
                                                                   entry_id=entry_id,
                                                                   scenario=scenario)

        # print(f"Entry ID : {entry_id}, Update Results Code: {update_results_response_code}")
        with data_lock:
            if update_results_response_code == 200 or update_results_response_code == 201:
                exp_data[experiment_name][KruizasterConsts.METADATA][KruizasterConsts.COMPLETED_ENTRIES] += 1
                exp_data[experiment_name][KruizasterConsts.METADATA][KruizasterConsts.UPDATE_RESULTS_SUCCESS] += 1
                exp_data[experiment_name][KruizasterConsts.METADATA][KruizasterConsts.UPDATE_RESULTS_FAILED] -= 1
            exp_data[experiment_name][KruizasterConsts.METADATA][KruizasterConsts.CURRENT_ENTRY] = entry_id

        # Check if day is greater than 1 and proceed to get recommendations
        if day > 1:
            end_time_string = entry_min_list[rec_counter][KruizasterConsts.INTERVAL_END_TIME]
            recommendation_response_code, recommendation_template = Utils.get_kruize_recommendations(
                                                                                exp_name=experiment_name,
                                                                                interval_end_time=end_time_string)
            recommendation_content = {
                KruizasterConsts.METADATA: {
                    KruizasterConsts.ENTRY_ID: entry_min_list[rec_counter][KruizasterConsts.ENTRY_ID],
                    KruizasterConsts.DAY: entry_min_list[rec_counter][KruizasterConsts.DAY],
                    KruizasterConsts.DAY_ENTRY_ID: entry_min_list[rec_counter][KruizasterConsts.DAY_ENTRY_ID]
                },
                KruizasterConsts.DATA: recommendation_template
            }

            rec_counter = rec_counter + 1
            with data_lock:
                exp_data[experiment_name][KruizasterConsts.KRUIZASTER_EXP_DATA][KruizasterConsts.KRUIZASTER_EXP_RECS][end_time_string] = recommendation_content
                exp_data[experiment_name][KruizasterConsts.METADATA][KruizasterConsts.RECOMMENDATIONS_GENERATED] = rec_counter

        with data_lock:
            if experiment_name in exp_data:
                total_entries = exp_data[experiment_name][KruizasterConsts.METADATA][KruizasterConsts.TOTAL_ENTRIES]
                current_update_entries = exp_data[experiment_name][KruizasterConsts.METADATA][KruizasterConsts.CURRENT_ENTRY]
                current_recommendation_entries = exp_data[experiment_name][KruizasterConsts.METADATA][KruizasterConsts.RECOMMENDATIONS_GENERATED]

                socket_data = {
                    KruizasterConsts.TOTAL_ENTRIES: total_entries,
                    KruizasterConsts.UPDATE_RESULTS_STATUS: {
                        KruizasterConsts.CURRENT_ENTRY: current_update_entries
                    },
                    KruizasterConsts.RECOMMENDATION_STATUS: {
                        KruizasterConsts.CURRENT_ENTRY: current_recommendation_entries
                    }
                }

                socket_data_str = json.dumps(socket_data).encode(KruizasterConsts.UTF_8)
                await websocket.send_text(socket_data_str)
                # As it's a single process and single threaded application we simulate a break in processing the results and sending the updates to socket
                # Should be changed when we read from DB and implement a multiprocess architecture
                await asyncio.sleep(0.01)


    for counter in range(rec_counter, len(entry_min_list)):
        end_time_string = entry_min_list[rec_counter][KruizasterConsts.INTERVAL_END_TIME]
        recommendation_response_code, recommendation_template = Utils.get_kruize_recommendations(
            exp_name=experiment_name,
            interval_end_time=end_time_string)
        recommendation_content = {
            KruizasterConsts.METADATA: {
                KruizasterConsts.ENTRY_ID: entry_min_list[rec_counter][KruizasterConsts.ENTRY_ID],
                KruizasterConsts.DAY: entry_min_list[rec_counter][KruizasterConsts.DAY],
                KruizasterConsts.DAY_ENTRY_ID: entry_min_list[rec_counter][KruizasterConsts.DAY_ENTRY_ID]
            },
            KruizasterConsts.DATA: recommendation_template
        }

        rec_counter = rec_counter + 1
        with data_lock:
            exp_data[experiment_name][KruizasterConsts.KRUIZASTER_EXP_DATA][KruizasterConsts.KRUIZASTER_EXP_RECS][end_time_string] = recommendation_content
            exp_data[experiment_name][KruizasterConsts.METADATA][KruizasterConsts.RECOMMENDATIONS_GENERATED] = rec_counter

        with data_lock:
            if experiment_name in exp_data:
                total_entries = exp_data[experiment_name][KruizasterConsts.METADATA][KruizasterConsts.TOTAL_ENTRIES]
                current_update_entries = exp_data[experiment_name][KruizasterConsts.METADATA][KruizasterConsts.CURRENT_ENTRY]
                current_recommendation_entries = exp_data[experiment_name][KruizasterConsts.METADATA][KruizasterConsts.RECOMMENDATIONS_GENERATED]

                socket_data = {
                    KruizasterConsts.TOTAL_ENTRIES: total_entries,
                    KruizasterConsts.UPDATE_RESULTS_STATUS: {
                        KruizasterConsts.CURRENT_ENTRY: current_update_entries
                    },
                    KruizasterConsts.RECOMMENDATION_STATUS: {
                        KruizasterConsts.CURRENT_ENTRY: current_recommendation_entries
                    }
                }

                socket_data_str = json.dumps(socket_data).encode(KruizasterConsts.UTF_8)
                await websocket.send_text(socket_data_str)
                # As it's a single process and single threaded application we simulate a break in processing the results and sending the updates to socket
                # Should be changed when we read from DB and implement a multiprocess architecture
                await asyncio.sleep(0.01)

    # Close websocket
    await websocket.close()


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


@app.get(KruizasterConsts.ServiceInfo.Kruizaster.ServicePaths.VIEW_EXPERIMENT)
async def view_experiment(request: Request, experiment_name: str):
    with data_lock:
        if experiment_name in exp_data:
            experiment_data = exp_data[experiment_name]
            entry_min_list = experiment_data[KruizasterConsts.METADATA][KruizasterConsts.ENTRY_MIN_LIST]
            interval_end_time = entry_min_list[0][KruizasterConsts.INTERVAL_END_TIME]
            update_results = experiment_data[KruizasterConsts.KRUIZASTER_EXP_DATA][KruizasterConsts.KRUIZASTER_EXP_RESULTS][interval_end_time]
            recommendations = experiment_data[KruizasterConsts.KRUIZASTER_EXP_DATA][KruizasterConsts.KRUIZASTER_EXP_RECS][interval_end_time]
            successful_entries = experiment_data[KruizasterConsts.METADATA][KruizasterConsts.UPDATE_RESULTS_SUCCESS]
            failed_entries = experiment_data[KruizasterConsts.METADATA][KruizasterConsts.UPDATE_RESULTS_FAILED]

            return templates.TemplateResponse(
                "view_experiment.html",
                {
                    "request": request,
                    "experiment_name": experiment_name,
                    "interval_end_time": interval_end_time,
                    "update_results": update_results,
                    "recommendations": recommendations,
                    "entry_min_list": entry_min_list,
                    "successful_entries": successful_entries,
                    "failed_entries": failed_entries,
                    "view_result_url": f"/view/{experiment_name}/result/{interval_end_time}"
                }
            )
    return templates.TemplateResponse(
        "error_page.html",
        {
            "request": request,
            "error_msg": f"Experiment Name : {experiment_name} is invalid",
            "return_url": KruizasterConsts.ServiceInfo.Kruizaster.ServicePaths.ROOT,
            "return_msg": KruizasterConsts.BACK_TO_HOME
        }
    )

@app.get(KruizasterConsts.ServiceInfo.Kruizaster.ServicePaths.VIEW_EXPERIMENT_RESULTS)
async def view_result(request: Request, experiment_name: str, interval_end_time: str):
    # Result JSON
    result_json = None
    # recommendation JSON
    recommendation_json = None
    # Entry MIN LIST
    entry_min_list = None
    # Acquire Lock to access the exp_data
    with data_lock:
        # Check if experiment name exists in experiment data
        if experiment_name in exp_data:
            # Get the entry min list
            entry_min_list = exp_data[experiment_name][KruizasterConsts.METADATA][KruizasterConsts.ENTRY_MIN_LIST]
            # get the results map
            results_map = exp_data[experiment_name][KruizasterConsts.KRUIZASTER_EXP_DATA][KruizasterConsts.KRUIZASTER_EXP_RESULTS]
            # get the recommendation map
            recommendations_map = exp_data[experiment_name][KruizasterConsts.KRUIZASTER_EXP_DATA][KruizasterConsts.KRUIZASTER_EXP_RECS]
            # Check if given interval exists for a experiment
            if interval_end_time in results_map and interval_end_time in recommendations_map:
                # Load results in to results JSON
                result_json = results_map[interval_end_time][KruizasterConsts.DATA]
                # Load recommedations to recommendation JSON
                recommendation_json = recommendations_map[interval_end_time][KruizasterConsts.DATA]
            else:
                # Return error saying the interval time is not found
                return templates.TemplateResponse(
                    "error_page.html",
                    {
                        "request": request,
                        "error_msg": f"Given Timestamp: {interval_end_time} is invalid for experiment : {experiment_name}",
                        "return_url": KruizasterConsts.ServiceInfo.Kruizaster.ServicePaths.ROOT,
                        "return_msg": KruizasterConsts.BACK_TO_HOME
                    }
                )
        else:
            # Return Experiment not available
            return templates.TemplateResponse(
                "error_page.html",
                {
                    "request": request,
                    "error_msg": f"Experiment Name : {experiment_name} is invalid",
                    "return_url": KruizasterConsts.ServiceInfo.Kruizaster.ServicePaths.ROOT,
                    "return_msg": KruizasterConsts.BACK_TO_HOME
                }
            )
        # Load all metrics
        metric_list = result_json[KruizasterConsts.KUBERNETES_OBJECTS][0][KruizasterConsts.CONTAINERS][0][KruizasterConsts.METRICS]
        # Content for update results table
        update_result_table = []
        # Entries for cpu results
        name_array_cpu = []
        sum_array_cpu = []
        avg_array_cpu = []
        min_array_cpu = []
        max_array_cpu = []
        # Entries for memory results
        name_array_memory = []
        sum_array_memory = []
        avg_array_memory = []
        min_array_memory = []
        max_array_memory = []
        # Short term CPU recommendation holder: [ CPU Request, CPU Limit, Current CPU Usage, Requests Variation, Limits Variation ]
        st_req_lim_cpu_arr = [None, None, None, None, None]
        # Short term Memory recommendation holder: [ Memory Request, Memory Limit, Current Memory Usage, Requests Variation, Limits Variation ]
        st_req_lim_memory_arr = [None, None, None, None, None]
        # Medium term CPU recommendation holder: [ CPU Request, CPU Limit, Current CPU Usage, Requests Variation, Limits Variation ]
        mt_req_lim_cpu_arr = [None, None, None, None, None]
        # Medium term Memory recommendation holder: [ Memory Request, Memory Limit, Current Memory Usage, Requests Variation, Limits Variation ]
        mt_req_lim_memory_arr = [None, None, None, None, None]
        # Long term CPU recommendation holder: [ CPU Request, CPU Limit, Current CPU Usage, Requests Variation, Limits Variation ]
        lt_req_lim_cpu_arr = [None, None, None, None, None]
        # Long term Memory recommendation holder: [ Memory Request, Memory Limit, Current Memory Usage, Requests Variation, Limits Variation ]
        lt_req_lim_memory_arr = [None, None, None, None, None]

        # Iterate over the metrics list to load contents to update results entries
        for entry in metric_list:
            # Format the contents in required way by calling "get_ui_update_result_entry" function in Utils
            update_result_entry = Utils.get_ui_update_result_entry(entry)
            # Check if the update_result_entry is not None (Highly impossible scenario, most unlikely to happen)
            if update_result_entry is not None:
                # Update the list and add the update_result_entry
                update_result_table.append(update_result_entry)
                # Extract the metric_name
                metric_name = update_result_entry[KruizasterConsts.NAME]
                # Check if metric_name is a CPU Metrics
                if metric_name in KruizasterConsts.CPU_METRICS:
                    # Add name to name array
                    name_array_cpu.append(metric_name)
                    # If sum exists load sum
                    if KruizasterConsts.SUM in update_result_entry:
                        sum_array_cpu.append(update_result_entry[KruizasterConsts.SUM])
                    else:
                        sum_array_cpu.append(None)
                    # If min exists load min
                    if KruizasterConsts.MIN in update_result_entry:
                        min_array_cpu.append(update_result_entry[KruizasterConsts.MIN])
                    else:
                        min_array_cpu.append(None)
                    # If avg exists load avg
                    if KruizasterConsts.AVG in update_result_entry:
                        avg_array_cpu.append(update_result_entry[KruizasterConsts.AVG])
                        # If the metric is cpu usage, record it in 3rd index of short term, medium term and long term
                        if metric_name == KruizasterConsts.CPU_USAGE:
                            st_req_lim_cpu_arr[2] = update_result_entry[KruizasterConsts.AVG]
                            mt_req_lim_cpu_arr[2] = update_result_entry[KruizasterConsts.AVG]
                            lt_req_lim_cpu_arr[2] = update_result_entry[KruizasterConsts.AVG]
                    else:
                        avg_array_cpu.append(None)
                    # If max exists load max
                    if KruizasterConsts.MAX in update_result_entry:
                        max_array_cpu.append(update_result_entry[KruizasterConsts.MAX])
                    else:
                        max_array_cpu.append(None)
                # Check if metric_name is a Memory Metrics
                if metric_name in KruizasterConsts.MEMORY_METRICS:
                    # Add name to name array
                    name_array_memory.append(metric_name)
                    # If sum exists load sum
                    if KruizasterConsts.SUM in update_result_entry:
                        sum_array_memory.append(update_result_entry[KruizasterConsts.SUM])
                    else:
                        sum_array_memory.append(None)
                    # If min exists load min
                    if KruizasterConsts.MIN in update_result_entry:
                        min_array_memory.append(update_result_entry[KruizasterConsts.MIN])
                    else:
                        min_array_memory.append(None)
                    # If avg exists load avg
                    if KruizasterConsts.AVG in update_result_entry:
                        avg_array_memory.append(update_result_entry[KruizasterConsts.AVG])
                        # If the metric is memory usage, record it in 3rd index of short term, medium term and long term
                        if metric_name == KruizasterConsts.MEMORY_USAGE:
                            st_req_lim_memory_arr[2] = update_result_entry[KruizasterConsts.AVG]
                            mt_req_lim_memory_arr[2] = update_result_entry[KruizasterConsts.AVG]
                            lt_req_lim_memory_arr[2] = update_result_entry[KruizasterConsts.AVG]
                    else:
                        avg_array_memory.append(None)
                    # If max exists load max
                    if KruizasterConsts.MAX in update_result_entry:
                        max_array_memory.append(update_result_entry[KruizasterConsts.MAX])
                    else:
                        max_array_memory.append(None)
        # Add the labels
        config_labels = ["Config Request", "Config Limit", "Current Usage", "Variation Request", "Variation Limit"]
        # chart data for short term cpu recommendations
        chart_data_rec_st_cpu = None
        # chart data for short term memory recommendations
        chart_data_rec_st_memory = None
        # chart data for medium term cpu recommendations
        chart_data_rec_mt_cpu = None
        # chart data for medium term memory recommendations
        chart_data_rec_mt_memory = None
        # chart data for long term cpu recommendations
        chart_data_rec_lt_cpu = None
        # chart data for long term memory recommendations
        chart_data_rec_lt_memory = None

        # Check if we have recommendation
        if KruizasterConsts.STATUS not in recommendation_json and KruizasterConsts.HTTP_CODE not in recommendation_json:
            recommendations = recommendation_json[KruizasterConsts.KUBERNETES_OBJECTS][0][KruizasterConsts.CONTAINERS][0][KruizasterConsts.RECOMMENDATIONS]
            # Check if we have recommendation
            if interval_end_time in recommendations[KruizasterConsts.DATA]:
                # Check if we have Duration based recommendations
                if KruizasterConsts.DURATION_BASED in recommendations[KruizasterConsts.DATA][interval_end_time]:
                    duration_based_rec = recommendations[KruizasterConsts.DATA][interval_end_time][KruizasterConsts.DURATION_BASED]
                    # Check if config is available short term
                    if KruizasterConsts.CONFIG in duration_based_rec[KruizasterConsts.SHORT_TERM]:
                        config = duration_based_rec[KruizasterConsts.SHORT_TERM][KruizasterConsts.CONFIG]
                        # Check if requests available
                        if KruizasterConsts.REQUESTS in config:
                            # Check if CPU requests available
                            if KruizasterConsts.CPU in config[KruizasterConsts.REQUESTS]:
                                st_req_lim_cpu_arr[0] = round(config[KruizasterConsts.REQUESTS][KruizasterConsts.CPU][KruizasterConsts.AMOUNT], 2)
                            # Check if Memory requests available
                            if KruizasterConsts.MEMORY in config[KruizasterConsts.REQUESTS]:
                                st_req_lim_memory_arr[0] = round(config[KruizasterConsts.REQUESTS][KruizasterConsts.MEMORY][KruizasterConsts.AMOUNT], 2)
                        # Check if limits available
                        if KruizasterConsts.LIMITS in config:
                            # Check if CPU Limits available
                            if KruizasterConsts.CPU in config[KruizasterConsts.LIMITS]:
                                st_req_lim_cpu_arr[1] = round(config[KruizasterConsts.LIMITS][KruizasterConsts.CPU][KruizasterConsts.AMOUNT], 2)
                            # Check if Memory Limits available
                            if KruizasterConsts.MEMORY in config[KruizasterConsts.LIMITS]:
                                st_req_lim_memory_arr[1] = round(config[KruizasterConsts.LIMITS][KruizasterConsts.MEMORY][KruizasterConsts.AMOUNT], 2)
                    # Check if variation is available in short term
                    if KruizasterConsts.VARIATION in duration_based_rec[KruizasterConsts.SHORT_TERM]:
                        variation = duration_based_rec[KruizasterConsts.SHORT_TERM][KruizasterConsts.VARIATION]
                        # Check if requests available
                        if KruizasterConsts.REQUESTS in variation:
                            # Check if CPU requests available
                            if KruizasterConsts.CPU in variation[KruizasterConsts.REQUESTS]:
                                st_req_lim_cpu_arr[3] = round(variation[KruizasterConsts.REQUESTS][KruizasterConsts.CPU][KruizasterConsts.AMOUNT], 2)
                            # Check if Memory requests available
                            if KruizasterConsts.MEMORY in variation[KruizasterConsts.REQUESTS]:
                                st_req_lim_memory_arr[3] = round(variation[KruizasterConsts.REQUESTS][KruizasterConsts.MEMORY][KruizasterConsts.AMOUNT], 2)
                        # Check if limits available
                        if KruizasterConsts.LIMITS in variation:
                            # Check if CPU Limits available
                            if KruizasterConsts.CPU in variation[KruizasterConsts.LIMITS]:
                                st_req_lim_cpu_arr[4] = round(variation[KruizasterConsts.LIMITS][KruizasterConsts.CPU][KruizasterConsts.AMOUNT], 2)
                            # Check if Memory Limits available
                            if KruizasterConsts.MEMORY in variation[KruizasterConsts.LIMITS]:
                                st_req_lim_memory_arr[4] = round(variation[KruizasterConsts.LIMITS][KruizasterConsts.MEMORY][KruizasterConsts.AMOUNT], 2)

                    # Check if config is available medium term
                    if KruizasterConsts.CONFIG in duration_based_rec[KruizasterConsts.MEDIUM_TERM]:
                        config = duration_based_rec[KruizasterConsts.MEDIUM_TERM][KruizasterConsts.CONFIG]
                        # Check if requests available
                        if KruizasterConsts.REQUESTS in config:
                            # Check if CPU requests available
                            if KruizasterConsts.CPU in config[KruizasterConsts.REQUESTS]:
                                mt_req_lim_cpu_arr[0] = round(
                                    config[KruizasterConsts.REQUESTS][KruizasterConsts.CPU][
                                        KruizasterConsts.AMOUNT], 2)
                            # Check if Memory requests available
                            if KruizasterConsts.MEMORY in config[KruizasterConsts.REQUESTS]:
                                mt_req_lim_memory_arr[0] = round(
                                    config[KruizasterConsts.REQUESTS][KruizasterConsts.MEMORY][
                                        KruizasterConsts.AMOUNT], 2)
                        # Check if limits available
                        if KruizasterConsts.LIMITS in config:
                            # Check if CPU Limits available
                            if KruizasterConsts.CPU in config[KruizasterConsts.LIMITS]:
                                mt_req_lim_cpu_arr[1] = round(
                                    config[KruizasterConsts.LIMITS][KruizasterConsts.CPU][
                                        KruizasterConsts.AMOUNT], 2)
                            # Check if Memory Limits available
                            if KruizasterConsts.MEMORY in config[KruizasterConsts.LIMITS]:
                                mt_req_lim_memory_arr[1] = round(
                                    config[KruizasterConsts.LIMITS][KruizasterConsts.MEMORY][
                                        KruizasterConsts.AMOUNT], 2)
                    # Check if variation is available in short term
                    if KruizasterConsts.VARIATION in duration_based_rec[KruizasterConsts.MEDIUM_TERM]:
                        variation = duration_based_rec[KruizasterConsts.MEDIUM_TERM][
                            KruizasterConsts.VARIATION]
                        # Check if requests available
                        if KruizasterConsts.REQUESTS in variation:
                            # Check if CPU requests available
                            if KruizasterConsts.CPU in variation[KruizasterConsts.REQUESTS]:
                                mt_req_lim_cpu_arr[3] = round(
                                    variation[KruizasterConsts.REQUESTS][KruizasterConsts.CPU][
                                        KruizasterConsts.AMOUNT], 2)
                            # Check if Memory requests available
                            if KruizasterConsts.MEMORY in variation[KruizasterConsts.REQUESTS]:
                                mt_req_lim_memory_arr[3] = round(
                                    variation[KruizasterConsts.REQUESTS][KruizasterConsts.MEMORY][
                                        KruizasterConsts.AMOUNT], 2)
                        # Check if limits available
                        if KruizasterConsts.LIMITS in variation:
                            # Check if CPU Limits available
                            if KruizasterConsts.CPU in variation[KruizasterConsts.LIMITS]:
                                mt_req_lim_cpu_arr[4] = round(
                                    variation[KruizasterConsts.LIMITS][KruizasterConsts.CPU][
                                        KruizasterConsts.AMOUNT], 2)
                            # Check if Memory Limits available
                            if KruizasterConsts.MEMORY in variation[KruizasterConsts.LIMITS]:
                                mt_req_lim_memory_arr[4] = round(
                                    variation[KruizasterConsts.LIMITS][KruizasterConsts.MEMORY][
                                        KruizasterConsts.AMOUNT], 2)

                    # Check if config is available Long Term
                    if KruizasterConsts.CONFIG in duration_based_rec[KruizasterConsts.LONG_TERM]:
                        config = duration_based_rec[KruizasterConsts.LONG_TERM][KruizasterConsts.CONFIG]
                        # Check if requests available
                        if KruizasterConsts.REQUESTS in config:
                            # Check if CPU requests available
                            if KruizasterConsts.CPU in config[KruizasterConsts.REQUESTS]:
                                lt_req_lim_cpu_arr[0] = round(
                                    config[KruizasterConsts.REQUESTS][KruizasterConsts.CPU][
                                        KruizasterConsts.AMOUNT], 2)
                            # Check if Memory requests available
                            if KruizasterConsts.MEMORY in config[KruizasterConsts.REQUESTS]:
                                lt_req_lim_memory_arr[0] = round(
                                    config[KruizasterConsts.REQUESTS][KruizasterConsts.MEMORY][
                                        KruizasterConsts.AMOUNT], 2)
                        # Check if limits available
                        if KruizasterConsts.LIMITS in config:
                            # Check if CPU Limits available
                            if KruizasterConsts.CPU in config[KruizasterConsts.LIMITS]:
                                lt_req_lim_cpu_arr[1] = round(
                                    config[KruizasterConsts.LIMITS][KruizasterConsts.CPU][
                                        KruizasterConsts.AMOUNT], 2)
                            # Check if Memory Limits available
                            if KruizasterConsts.MEMORY in config[KruizasterConsts.LIMITS]:
                                lt_req_lim_memory_arr[1] = round(
                                    config[KruizasterConsts.LIMITS][KruizasterConsts.MEMORY][
                                        KruizasterConsts.AMOUNT], 2)
                    # Check if variation is available in Long Term
                    if KruizasterConsts.VARIATION in duration_based_rec[KruizasterConsts.LONG_TERM]:
                        variation = duration_based_rec[KruizasterConsts.LONG_TERM][
                            KruizasterConsts.VARIATION]
                        # Check if requests available
                        if KruizasterConsts.REQUESTS in variation:
                            # Check if CPU requests available
                            if KruizasterConsts.CPU in variation[KruizasterConsts.REQUESTS]:
                                lt_req_lim_cpu_arr[3] = round(
                                    variation[KruizasterConsts.REQUESTS][KruizasterConsts.CPU][
                                        KruizasterConsts.AMOUNT], 2)
                            # Check if Memory requests available
                            if KruizasterConsts.MEMORY in variation[KruizasterConsts.REQUESTS]:
                                lt_req_lim_memory_arr[3] = round(
                                    variation[KruizasterConsts.REQUESTS][KruizasterConsts.MEMORY][
                                        KruizasterConsts.AMOUNT], 2)
                        # Check if limits available
                        if KruizasterConsts.LIMITS in variation:
                            # Check if CPU Limits available
                            if KruizasterConsts.CPU in variation[KruizasterConsts.LIMITS]:
                                lt_req_lim_cpu_arr[4] = round(
                                    variation[KruizasterConsts.LIMITS][KruizasterConsts.CPU][
                                        KruizasterConsts.AMOUNT], 2)
                            # Check if Memory Limits available
                            if KruizasterConsts.MEMORY in variation[KruizasterConsts.LIMITS]:
                                lt_req_lim_memory_arr[4] = round(
                                    variation[KruizasterConsts.LIMITS][KruizasterConsts.MEMORY][
                                        KruizasterConsts.AMOUNT], 2)
                    chart_data_rec_st_cpu = {
                        "labels": config_labels,
                        "data": st_req_lim_cpu_arr
                    }
                    chart_data_rec_st_memory = {
                        "labels": config_labels,
                        "data": st_req_lim_memory_arr
                    }
                    chart_data_rec_mt_cpu = {
                        "labels": config_labels,
                        "data": mt_req_lim_cpu_arr
                    }
                    chart_data_rec_mt_memory = {
                        "labels": config_labels,
                        "data": mt_req_lim_memory_arr
                    }
                    chart_data_rec_lt_cpu = {
                        "labels": config_labels,
                        "data": lt_req_lim_cpu_arr
                    }
                    chart_data_rec_lt_memory = {
                        "labels": config_labels,
                        "data": lt_req_lim_memory_arr
                    }


        chart_data_cpu = {
            KruizasterConsts.NAME: name_array_cpu,
            KruizasterConsts.SUM: sum_array_cpu,
            KruizasterConsts.MIN: min_array_cpu,
            KruizasterConsts.AVG: avg_array_cpu,
            KruizasterConsts.MAX: max_array_cpu
        }

        chart_data_memory = {
            KruizasterConsts.NAME: name_array_memory,
            KruizasterConsts.SUM: sum_array_memory,
            KruizasterConsts.MIN: min_array_memory,
            KruizasterConsts.AVG: avg_array_memory,
            KruizasterConsts.MAX: max_array_memory
        }
        return templates.TemplateResponse(
            "view_result.html",
            {
                "request": request,
                "experiment_name": experiment_name,
                "interval_end_time": interval_end_time,
                "entry_min_list": entry_min_list,
                "result_json": result_json,
                "recommendation_json": recommendation_json,
                "update_result_table": update_result_table,
                "chart_data_cpu": chart_data_cpu,
                "chart_data_memory": chart_data_memory,
                "chart_data_rec_st_cpu": chart_data_rec_st_cpu,
                "chart_data_rec_st_memory": chart_data_rec_st_memory,
                "chart_data_rec_mt_cpu": chart_data_rec_mt_cpu,
                "chart_data_rec_mt_memory": chart_data_rec_mt_memory,
                "chart_data_rec_lt_cpu": chart_data_rec_lt_cpu,
                "chart_data_rec_lt_memory": chart_data_rec_lt_memory
            }
        )


@app.get(KruizasterConsts.ServiceInfo.Kruizaster.ServicePaths.LIST_EXPERIMENTS)
async def list_experiments(request: Request):
    exp_metadata_list = []
    with data_lock:
        for experiment_name, experiment_data in exp_data.items():
            metadata = {
                "experiment_name": experiment_name,
                "entries": exp_data[experiment_name][KruizasterConsts.METADATA][KruizasterConsts.TOTAL_ENTRIES],
                "success": exp_data[experiment_name][KruizasterConsts.METADATA][KruizasterConsts.UPDATE_RESULTS_SUCCESS],
                "failed": exp_data[experiment_name][KruizasterConsts.METADATA][KruizasterConsts.UPDATE_RESULTS_FAILED],
                "num_days": exp_data[experiment_name][KruizasterConsts.METADATA][KruizasterConsts.NUM_DAYS],
                "scenario": exp_data[experiment_name][KruizasterConsts.METADATA][KruizasterConsts.SCENARIO],
                "path": f"/view/{experiment_name}"
            }
            exp_metadata_list.append(metadata)

    return templates.TemplateResponse(
        "list_experiments.html",
        {
            "request": request,
            "exp_data_list": exp_metadata_list
        }
    )


@app.websocket(KruizasterConsts.ServiceInfo.Kruizaster.ServicePaths.UPDATES_SOCKET)
async def updates_endpoint(websocket: WebSocket, experiment_name: str):
    await websocket.accept()
    print(f"Experiment Name : {experiment_name}")
    if experiment_name is not None:
        proceed = False
        scenario = None
        with data_lock:
            if experiment_name in exp_data:
                scenario = exp_data[experiment_name][KruizasterConsts.METADATA][KruizasterConsts.SCENARIO]
                if scenario in KruizasterConsts.SCENARIOS:
                    proceed = True
        if proceed and scenario is not None:
            # Create a background task
            bg_task = asyncio.create_task(process_create_exp_update_results(websocket=websocket,
                                                                            experiment_name=experiment_name,
                                                                            scenario=scenario))
            try:
                await bg_task
            except WebSocketDisconnect:
                # Cancel the data processing task if the WebSocket connection is disconnected
                bg_task.cancel()
                await bg_task


@app.post(KruizasterConsts.ServiceInfo.Kruizaster.ServicePaths.CREATE_DISASTER)
async def generate_jsons(request: Request,
                         experiment_name: str = Form(...),
                         num_days: int = Form(...),
                         start_time: datetime = Form(...),
                         scenario: str = Form(...),
                         interval_duration: str = Form(...)):
    experiment_name                 = experiment_name.strip()
    interval_duration               = interval_duration.strip()
    total_duration_in_mins          = num_days * 24 * 60
    total_entries                   = 0
    interval_time                   = 0
    interval_unit                   = ""
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

    scenario = scenario.strip()
    if scenario not in KruizasterConsts.SCENARIOS:
        scenario = KruizasterConsts.NO_DISASTER

    # Check if experiment name is not None
    if experiment_name is not None or experiment_name != "":

        # Create Experiment
        create_exp_response, return_json = Utils.create_kruize_experiment(exp_name=experiment_name,
                                                                          interval_time_in_mins=interval_time_in_mins,
                                                                          scenario=scenario)

        # Check if experiment is created
        if create_exp_response == 200 or create_exp_response == 201:
            # Create a gate to check of experiment exists (so that we won't lock for creation process)
            is_exists = True

            # Acquire lock
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
                        KruizasterConsts.INTERVAL_END_TIME: end_time_string
                    })
                    # The future has become present (It's jus we are progressing to next iteration)
                    entry_start_time = entry_end_time

                # Create a template for experiment schema to store in dict
                exp_data_content = {
                    KruizasterConsts.METADATA: {
                        KruizasterConsts.EXPERIMENT_NAME: experiment_name.strip(),
                        KruizasterConsts.STATUS: KruizasterConsts.CREATING,
                        KruizasterConsts.TOTAL_DURATION: total_duration_in_mins,
                        KruizasterConsts.MEASUREMENT_DURATION: interval_time_in_mins,
                        KruizasterConsts.TOTAL_ENTRIES: total_entries,
                        KruizasterConsts.NUM_DAYS: num_days,
                        KruizasterConsts.CURRENT_ENTRY: 1,
                        KruizasterConsts.COMPLETED_ENTRIES: 0,
                        KruizasterConsts.ENTRY_MIN_LIST: entry_min_list,
                        KruizasterConsts.RECOMMENDATIONS_GENERATED: 0,
                        KruizasterConsts.UPDATE_RESULTS_SUCCESS: 0,
                        KruizasterConsts.UPDATE_RESULTS_FAILED: total_entries,
                        KruizasterConsts.SCENARIO: scenario.strip()
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
                # Acquire lock and push the template and tag to the experiment name
                with data_lock:
                    exp_data[experiment_name] = exp_data_content

            return templates.TemplateResponse(
                "process_updates.html",
                {
                    "request": request,
                    "experiment_name": experiment_name,
                    "total_entries": len(entry_min_list)
                }
            )
        else:
            return templates.TemplateResponse(
                "error_page.html",
                {
                    "request": request,
                    "error_msg": return_json[KruizasterConsts.MESSAGE],
                    "return_url": KruizasterConsts.ServiceInfo.Kruizaster.ServicePaths.ROOT,
                    "return_msg": KruizasterConsts.BACK_TO_HOME
                }
            )


def shutdown_handler(signum, frame):
    # Add any clean up we need for data structures to release memory
    exit(0)


def create_app():
    return app


if __name__ == "__main__":
    # Register signal handlers for clean shutdown
    signal.signal(signal.SIGINT, shutdown_handler)
    signal.signal(signal.SIGTERM, shutdown_handler)

    try:
        # Start the FastAPI application with Uvicorn
        uvicorn.run("main:create_app", host="0.0.0.0", port=8000, workers=1)
    except SystemExit:
        # Clean up the shared memory in case of normal exit
        exit(0)



