import json

from consts.cnario_consts import Constants as KruizasterConsts
from kruizaster.settings import KruizasterSettings
from datetime import date, datetime
import random
import sys
import string
import requests
import httpx

METRIC_VALUE_MAP = {
    KruizasterConsts.CPU_REQUEST: {
        KruizasterConsts.AVAILABLE_FUNCS: [
            KruizasterConsts.SUM,
            KruizasterConsts.AVG
        ]
    },
    KruizasterConsts.CPU_LIMIT: {
        KruizasterConsts.AVAILABLE_FUNCS: [
            KruizasterConsts.SUM,
            KruizasterConsts.AVG
        ]
    },
    KruizasterConsts.CPU_USAGE: {
        KruizasterConsts.AVAILABLE_FUNCS: [
            KruizasterConsts.SUM,
            KruizasterConsts.AVG,
            KruizasterConsts.MIN,
            KruizasterConsts.MAX
        ]
    },
    KruizasterConsts.CPU_THROTTLE: {
        KruizasterConsts.AVAILABLE_FUNCS: [
            KruizasterConsts.SUM,
            KruizasterConsts.AVG,
            KruizasterConsts.MAX
        ]
    },
    KruizasterConsts.MEMORY_REQUEST: {
        KruizasterConsts.AVAILABLE_FUNCS: [
            KruizasterConsts.SUM,
            KruizasterConsts.AVG
        ]
    },
    KruizasterConsts.MEMORY_LIMIT: {
        KruizasterConsts.AVAILABLE_FUNCS: [
            KruizasterConsts.SUM,
            KruizasterConsts.AVG
        ]
    },
    KruizasterConsts.MEMORY_USAGE: {
        KruizasterConsts.AVAILABLE_FUNCS: [
            KruizasterConsts.SUM,
            KruizasterConsts.AVG,
            KruizasterConsts.MIN,
            KruizasterConsts.MAX
        ]
    },
    KruizasterConsts.MEMORY_RSS: {
        KruizasterConsts.AVAILABLE_FUNCS: [
            KruizasterConsts.SUM,
            KruizasterConsts.AVG,
            KruizasterConsts.MIN,
            KruizasterConsts.MAX
        ]
    },
}


def get_random_exp_name():
    adjective = random.choice(KruizasterConsts.ADJECTIVES)
    name = random.choice(KruizasterConsts.NAMES)
    return f"{adjective}-{name}"


def format_date_to_standard_string(date_passed: datetime):
    microseconds = date_passed.strftime("%f")[:3]
    return date_passed.strftime(KruizasterConsts.KRUIZE_PARTIAL_FORMAT) + "." + microseconds + KruizasterConsts.Z_FORMAT


def generate_random_float(min_passed=0, max_passed=sys.maxsize, precision=2):
    random_float = round(random.uniform(min_passed, max_passed), precision)
    return random_float


def generate_random_int(min_passed=0, max_passed=sys.maxsize):
    random_int = random.randint(min_passed, max_passed)
    return random_int


def generate_random_string(length):
    letters = string.ascii_letters
    random_string = ''.join(random.choice(letters) for _ in range(length))
    return random_string


def get_metric_data_template(metric: str, values: dict):
    if metric not in KruizasterConsts.ALL_METRICS:
        return None
    metric_data = {
        KruizasterConsts.NAME: metric,
        KruizasterConsts.RESULTS: {
            KruizasterConsts.VALUE: values[KruizasterConsts.VALUE],
            KruizasterConsts.FORMAT: "cores" if metric in KruizasterConsts.CPU_METRICS else "MiB",
            KruizasterConsts.AGGREGATION_INFO: {
                KruizasterConsts.FORMAT: "cores" if metric in KruizasterConsts.CPU_METRICS else "MiB"
            }
        }
    }

    for func in METRIC_VALUE_MAP[metric][KruizasterConsts.AVAILABLE_FUNCS]:
        metric_data[KruizasterConsts.RESULTS][KruizasterConsts.AGGREGATION_INFO][func] = values[func]

    return metric_data


def get_ui_update_result_entry(metric_data: dict):
    metric_name = metric_data[KruizasterConsts.NAME]
    update_result_entry = {
        KruizasterConsts.NAME: metric_name
    }
    for func in METRIC_VALUE_MAP[metric_name][KruizasterConsts.AVAILABLE_FUNCS]:
        update_result_entry[func] = metric_data[KruizasterConsts.RESULTS][KruizasterConsts.AGGREGATION_INFO][func]

    return update_result_entry


def create_kruize_experiment(exp_name: str, interval_time_in_mins: int):
    json_data = [{
        "version": "1.0",
        "experiment_name": exp_name,
        "cluster_name": "cluster-one-division-bell",
        "performance_profile": "resource-optimization-openshift",
        "mode": "monitor",
        "target_cluster": "remote",
        "kubernetes_objects": [
            {
                "type": KruizasterConsts.DEPLOYMENT,
                "name": KruizasterConsts.SAMPLE_DEPLOYMENT,
                "namespace": KruizasterConsts.DEFAULT,
                "containers": [
                    {
                        "container_image_name": KruizasterConsts.SAMPLE_IMAGE,
                        "container_name": KruizasterConsts.SAMPLE_CONTAINER
                    }
                ]
            }
        ],
        "trial_settings": {
            "measurement_duration": str(interval_time_in_mins) + "min"
        },
        "recommendation_settings": {
            "threshold": "0.1"
        }
    }]
    response = requests.post(KruizasterSettings.KRUIZE_CREATE_EXP_URL, json=json_data)

    if response.status_code == 200 or response.status_code == 201:
        #print(f"Created Experiment with name {exp_name} successfully")
        pass
    else:
        #print(f"Error occurred in creating experiment with name {exp_name}. Response code:  {response.status_code}")
        pass

    return response.status_code, response.json()


def update_kruize_results(results: dict, exp_name: str, interval_end_time: str):
    results = [results]
    response = requests.post(KruizasterSettings.KRUIZE_UPDATE_RESULTS_URL, json=results)

    if response.status_code == 200 or response.status_code == 201:
        #print(f"Updated Results successfully for Experiment : {exp_name} and for timestamp : {interval_end_time}")
        pass
    else:
        #print(f"Error occurred in updating results for Experiment : {exp_name} and for timestamp : {interval_end_time}"
              #+ f" with status code: {response.status_code}")
        pass
    return response.status_code


def get_url_with_params(base_url: str, params: dict):
    if len(params) > 0:
        url = base_url
        check_first = True
        for key, value in params.items():
            if check_first:
                url = url + KruizasterConsts.URL_PARAM_SPECIFIER + key + KruizasterConsts.URL_PARAM_VALUE_EQUAL + value
                check_first = False
            else:
                url = url + KruizasterConsts.URL_PARAM_ADDER + key + KruizasterConsts.URL_PARAM_VALUE_EQUAL + value
        return url
    else:
        return base_url


def get_kruize_recommendations(exp_name: str, interval_end_time: str):
    url_to_hit = get_url_with_params(
            base_url=KruizasterSettings.KRUIZE_LIST_REC_URL,
            params={
                KruizasterConsts.EXPERIMENT_NAME: exp_name,
                KruizasterConsts.MONITORING_END_TIME: interval_end_time
            }
        )

    response = requests.get(url_to_hit)
    return_val = None
    if response.status_code == 200 or response.status_code == 201:
        return_val = response.json()
        if isinstance(return_val, list):
            if len(return_val) > 0:
                return_val = return_val[0]
    else:
        return_val = response.json()
    return response.status_code, return_val
