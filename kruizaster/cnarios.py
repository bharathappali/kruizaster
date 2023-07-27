from consts.cnario_consts import Constants as KruizasterConsts
from kruizaster import utils as Utils


def get_results_of_scenario(scenario: str, metric: str):
    sum_field = avg_field = min_field = max_field = value_field = KruizasterConsts.ZERO_VAL
    # Set anything default to NO DISASTER
    if scenario not in KruizasterConsts.SCENARIOS:
        scenario = KruizasterConsts.NO_DISASTER

    # Generate fields for Default and No Disaster Scenario
    if scenario == KruizasterConsts.DEFAULT or scenario == KruizasterConsts.NO_DISASTER:
        # Generate CPU Fields
        if metric in KruizasterConsts.CPU_METRICS:
            avg_field = Utils.generate_random_float(KruizasterConsts.MIN_AVG_CPU,
                                                    KruizasterConsts.MAX_AVG_CPU)
            sum_field = Utils.generate_random_int(KruizasterConsts.MIN_PODS,
                                            KruizasterConsts.MAX_PODS) * avg_field

            max_field = Utils.generate_random_float(avg_field,
                                                    KruizasterConsts.MAX_MAX_CPU)

            min_field = Utils.generate_random_float(KruizasterConsts.MIN_MIN_CPU,
                                                    avg_field)

            value_field = Utils.generate_random_float(KruizasterConsts.MIN_CPU,
                                                      KruizasterConsts.MAX_CPU)
        # Generate Memory Fields
        elif metric in KruizasterConsts.MEMORY_METRICS:
            avg_field = Utils.generate_random_float(KruizasterConsts.MIN_AVG_MEMORY,
                                                    KruizasterConsts.MAX_AVG_MEMORY)
            sum_field = Utils.generate_random_int(KruizasterConsts.MIN_PODS,
                                                  KruizasterConsts.MAX_PODS) * avg_field

            max_field = Utils.generate_random_float(avg_field,
                                                    KruizasterConsts.MAX_MAX_MEMORY)

            min_field = Utils.generate_random_float(KruizasterConsts.MIN_MIN_MEMORY,
                                                    avg_field)

            value_field = Utils.generate_random_float(KruizasterConsts.MIN_MEMORY,
                                                      KruizasterConsts.MAX_MEMORY)
    # Generate fields for Zero cpu values Scenario
    elif scenario == KruizasterConsts.ZERO_CPUS_RECORDS:
        if metric in KruizasterConsts.MEMORY_METRICS:
            avg_field = Utils.generate_random_float(KruizasterConsts.MIN_AVG_MEMORY,
                                                    KruizasterConsts.MAX_AVG_MEMORY)
            sum_field = Utils.generate_random_int(KruizasterConsts.MIN_PODS,
                                                  KruizasterConsts.MAX_PODS) * avg_field

            max_field = Utils.generate_random_float(avg_field,
                                                    KruizasterConsts.MAX_MAX_MEMORY)

            min_field = Utils.generate_random_float(KruizasterConsts.MIN_MIN_MEMORY,
                                                    avg_field)

            value_field = Utils.generate_random_float(KruizasterConsts.MIN_MEMORY,
                                                      KruizasterConsts.MAX_MEMORY)
    # Generate fields for Zero memory Scenario
    elif scenario == KruizasterConsts.ZERO_MEMORY_RECORDS:
        if metric in KruizasterConsts.CPU_METRICS:
            avg_field = Utils.generate_random_float(KruizasterConsts.MIN_AVG_CPU,
                                                    KruizasterConsts.MAX_AVG_CPU)
            sum_field = Utils.generate_random_int(KruizasterConsts.MIN_PODS,
                                                  KruizasterConsts.MAX_PODS) * avg_field

            max_field = Utils.generate_random_float(avg_field,
                                                    KruizasterConsts.MAX_MAX_CPU)

            min_field = Utils.generate_random_float(KruizasterConsts.MIN_MIN_CPU,
                                                    avg_field)

            value_field = Utils.generate_random_float(KruizasterConsts.MIN_CPU,
                                                      KruizasterConsts.MAX_CPU)
    # Generate fields for Idle CPU Scenario
    elif scenario == KruizasterConsts.IDLE_CPU:
        if metric in KruizasterConsts.CPU_METRICS:
            avg_field = Utils.generate_random_float(KruizasterConsts.IDLE_CPU_MIN,
                                                    KruizasterConsts.IDLE_CPU_MAX,
                                                    8)
            sum_field = Utils.generate_random_int(KruizasterConsts.MIN_PODS,
                                                  KruizasterConsts.MAX_PODS) * avg_field

            max_field = Utils.generate_random_float(KruizasterConsts.IDLE_CPU_MIN,
                                                    KruizasterConsts.IDLE_CPU_MAX,
                                                    8)

            min_field = Utils.generate_random_float(KruizasterConsts.IDLE_CPU_MIN,
                                                    max_field,
                                                    8)

            value_field = Utils.generate_random_float(KruizasterConsts.IDLE_CPU_MIN,
                                                    KruizasterConsts.IDLE_CPU_MAX,
                                                      8)
        if metric in KruizasterConsts.MEMORY_METRICS:
            avg_field = Utils.generate_random_float(KruizasterConsts.MIN_AVG_MEMORY,
                                                    KruizasterConsts.MAX_AVG_MEMORY)
            sum_field = Utils.generate_random_int(KruizasterConsts.MIN_PODS,
                                                  KruizasterConsts.MAX_PODS) * avg_field

            max_field = Utils.generate_random_float(avg_field,
                                                    KruizasterConsts.MAX_MAX_MEMORY)

            min_field = Utils.generate_random_float(KruizasterConsts.MIN_MIN_MEMORY,
                                                    avg_field)

            value_field = Utils.generate_random_float(KruizasterConsts.MIN_MEMORY,
                                                      KruizasterConsts.MAX_MEMORY)

    elif scenario == KruizasterConsts.MEMORY_METRICS_MISSING:
        if metric in KruizasterConsts.CPU_METRICS:
            avg_field = Utils.generate_random_float(KruizasterConsts.MIN_AVG_CPU,
                                                    KruizasterConsts.MAX_AVG_CPU)
            sum_field = Utils.generate_random_int(KruizasterConsts.MIN_PODS,
                                                  KruizasterConsts.MAX_PODS) * avg_field

            max_field = Utils.generate_random_float(avg_field,
                                                    KruizasterConsts.MAX_MAX_CPU)

            min_field = Utils.generate_random_float(KruizasterConsts.MIN_MIN_CPU,
                                                    avg_field)

            value_field = Utils.generate_random_float(KruizasterConsts.MIN_CPU,
                                                      KruizasterConsts.MAX_CPU)
        else:
            return None

    elif scenario == KruizasterConsts.CPU_METRICS_MISSING:
        if metric in KruizasterConsts.MEMORY_METRICS:
            avg_field = Utils.generate_random_float(KruizasterConsts.MIN_AVG_MEMORY,
                                                    KruizasterConsts.MAX_AVG_MEMORY)
            sum_field = Utils.generate_random_int(KruizasterConsts.MIN_PODS,
                                                  KruizasterConsts.MAX_PODS) * avg_field

            max_field = Utils.generate_random_float(avg_field,
                                                    KruizasterConsts.MAX_MAX_MEMORY)

            min_field = Utils.generate_random_float(KruizasterConsts.MIN_MIN_MEMORY,
                                                    avg_field)

            value_field = Utils.generate_random_float(KruizasterConsts.MIN_MEMORY,
                                                      KruizasterConsts.MAX_MEMORY)
        else:
            return None

    elif scenario == KruizasterConsts.CPU_REQUEST_NOT_SET:
        if metric == KruizasterConsts.CPU_REQUEST:
            return None
        if metric in KruizasterConsts.CPU_METRICS:
            avg_field = Utils.generate_random_float(KruizasterConsts.MIN_AVG_CPU,
                                                    KruizasterConsts.MAX_AVG_CPU)
            sum_field = Utils.generate_random_int(KruizasterConsts.MIN_PODS,
                                                  KruizasterConsts.MAX_PODS) * avg_field

            max_field = Utils.generate_random_float(avg_field,
                                                    KruizasterConsts.MAX_MAX_CPU)

            min_field = Utils.generate_random_float(KruizasterConsts.MIN_MIN_CPU,
                                                    avg_field)

            value_field = Utils.generate_random_float(KruizasterConsts.MIN_CPU,
                                                      KruizasterConsts.MAX_CPU)

        if metric in KruizasterConsts.MEMORY_METRICS:
            avg_field = Utils.generate_random_float(KruizasterConsts.MIN_AVG_MEMORY,
                                                    KruizasterConsts.MAX_AVG_MEMORY)
            sum_field = Utils.generate_random_int(KruizasterConsts.MIN_PODS,
                                                  KruizasterConsts.MAX_PODS) * avg_field

            max_field = Utils.generate_random_float(avg_field,
                                                    KruizasterConsts.MAX_MAX_MEMORY)

            min_field = Utils.generate_random_float(KruizasterConsts.MIN_MIN_MEMORY,
                                                    avg_field)

            value_field = Utils.generate_random_float(KruizasterConsts.MIN_MEMORY,
                                                      KruizasterConsts.MAX_MEMORY)

    elif scenario == KruizasterConsts.CPU_LIMIT_NOT_SET:
        if metric == KruizasterConsts.CPU_LIMIT:
            return None
        if metric in KruizasterConsts.CPU_METRICS:
            avg_field = Utils.generate_random_float(KruizasterConsts.MIN_AVG_CPU,
                                                    KruizasterConsts.MAX_AVG_CPU)
            sum_field = Utils.generate_random_int(KruizasterConsts.MIN_PODS,
                                                  KruizasterConsts.MAX_PODS) * avg_field

            max_field = Utils.generate_random_float(avg_field,
                                                    KruizasterConsts.MAX_MAX_CPU)

            min_field = Utils.generate_random_float(KruizasterConsts.MIN_MIN_CPU,
                                                    avg_field)

            value_field = Utils.generate_random_float(KruizasterConsts.MIN_CPU,
                                                      KruizasterConsts.MAX_CPU)

        if metric in KruizasterConsts.MEMORY_METRICS:
            avg_field = Utils.generate_random_float(KruizasterConsts.MIN_AVG_MEMORY,
                                                    KruizasterConsts.MAX_AVG_MEMORY)
            sum_field = Utils.generate_random_int(KruizasterConsts.MIN_PODS,
                                                  KruizasterConsts.MAX_PODS) * avg_field

            max_field = Utils.generate_random_float(avg_field,
                                                    KruizasterConsts.MAX_MAX_MEMORY)

            min_field = Utils.generate_random_float(KruizasterConsts.MIN_MIN_MEMORY,
                                                    avg_field)

            value_field = Utils.generate_random_float(KruizasterConsts.MIN_MEMORY,
                                                      KruizasterConsts.MAX_MEMORY)

    elif scenario == KruizasterConsts.MEMORY_REQUEST_NOT_SET:
        if metric == KruizasterConsts.MEMORY_REQUEST:
            return None
        if metric in KruizasterConsts.CPU_METRICS:
            avg_field = Utils.generate_random_float(KruizasterConsts.MIN_AVG_CPU,
                                                    KruizasterConsts.MAX_AVG_CPU)
            sum_field = Utils.generate_random_int(KruizasterConsts.MIN_PODS,
                                                  KruizasterConsts.MAX_PODS) * avg_field

            max_field = Utils.generate_random_float(avg_field,
                                                    KruizasterConsts.MAX_MAX_CPU)

            min_field = Utils.generate_random_float(KruizasterConsts.MIN_MIN_CPU,
                                                    avg_field)

            value_field = Utils.generate_random_float(KruizasterConsts.MIN_CPU,
                                                      KruizasterConsts.MAX_CPU)

        if metric in KruizasterConsts.MEMORY_METRICS:
            avg_field = Utils.generate_random_float(KruizasterConsts.MIN_AVG_MEMORY,
                                                    KruizasterConsts.MAX_AVG_MEMORY)
            sum_field = Utils.generate_random_int(KruizasterConsts.MIN_PODS,
                                                  KruizasterConsts.MAX_PODS) * avg_field

            max_field = Utils.generate_random_float(avg_field,
                                                    KruizasterConsts.MAX_MAX_MEMORY)

            min_field = Utils.generate_random_float(KruizasterConsts.MIN_MIN_MEMORY,
                                                    avg_field)

            value_field = Utils.generate_random_float(KruizasterConsts.MIN_MEMORY,
                                                      KruizasterConsts.MAX_MEMORY)

    elif scenario == KruizasterConsts.MEMORY_LIMIT_NOT_SET:
        if metric == KruizasterConsts.MEMORY_LIMIT:
            return None
        if metric in KruizasterConsts.CPU_METRICS:
            avg_field = Utils.generate_random_float(KruizasterConsts.MIN_AVG_CPU,
                                                    KruizasterConsts.MAX_AVG_CPU)
            sum_field = Utils.generate_random_int(KruizasterConsts.MIN_PODS,
                                                  KruizasterConsts.MAX_PODS) * avg_field

            max_field = Utils.generate_random_float(avg_field,
                                                    KruizasterConsts.MAX_MAX_CPU)

            min_field = Utils.generate_random_float(KruizasterConsts.MIN_MIN_CPU,
                                                    avg_field)

            value_field = Utils.generate_random_float(KruizasterConsts.MIN_CPU,
                                                      KruizasterConsts.MAX_CPU)

        if metric in KruizasterConsts.MEMORY_METRICS:
            avg_field = Utils.generate_random_float(KruizasterConsts.MIN_AVG_MEMORY,
                                                    KruizasterConsts.MAX_AVG_MEMORY)
            sum_field = Utils.generate_random_int(KruizasterConsts.MIN_PODS,
                                                  KruizasterConsts.MAX_PODS) * avg_field

            max_field = Utils.generate_random_float(avg_field,
                                                    KruizasterConsts.MAX_MAX_MEMORY)

            min_field = Utils.generate_random_float(KruizasterConsts.MIN_MIN_MEMORY,
                                                    avg_field)

            value_field = Utils.generate_random_float(KruizasterConsts.MIN_MEMORY,
                                                      KruizasterConsts.MAX_MEMORY)
    elif scenario == KruizasterConsts.ONLY_REQUIRED_SET:
        if metric not in KruizasterConsts.REQUIRED_METRICS:
            return None
        if metric in KruizasterConsts.CPU_METRICS:
            avg_field = Utils.generate_random_float(KruizasterConsts.MIN_AVG_CPU,
                                                    KruizasterConsts.MAX_AVG_CPU)
            sum_field = Utils.generate_random_int(KruizasterConsts.MIN_PODS,
                                                  KruizasterConsts.MAX_PODS) * avg_field

            max_field = Utils.generate_random_float(avg_field,
                                                    KruizasterConsts.MAX_MAX_CPU)

            min_field = Utils.generate_random_float(KruizasterConsts.MIN_MIN_CPU,
                                                    avg_field)

            value_field = Utils.generate_random_float(KruizasterConsts.MIN_CPU,
                                                      KruizasterConsts.MAX_CPU)

        if metric in KruizasterConsts.MEMORY_METRICS:
            avg_field = Utils.generate_random_float(KruizasterConsts.MIN_AVG_MEMORY,
                                                    KruizasterConsts.MAX_AVG_MEMORY)
            sum_field = Utils.generate_random_int(KruizasterConsts.MIN_PODS,
                                                  KruizasterConsts.MAX_PODS) * avg_field

            max_field = Utils.generate_random_float(avg_field,
                                                    KruizasterConsts.MAX_MAX_MEMORY)

            min_field = Utils.generate_random_float(KruizasterConsts.MIN_MIN_MEMORY,
                                                    avg_field)

            value_field = Utils.generate_random_float(KruizasterConsts.MIN_MEMORY,
                                                      KruizasterConsts.MAX_MEMORY)
    elif scenario == KruizasterConsts.RESOURCE_OPTIMISED:
        if metric in KruizasterConsts.CPU_METRICS and metric is not KruizasterConsts.CPU_THROTTLE:
            avg_field = KruizasterConsts.OPTIMISED_CPU
            sum_field = avg_field
            max_field = avg_field
            min_field = avg_field
            value_field = avg_field
        if metric in KruizasterConsts.MEMORY_METRICS:
            avg_field = KruizasterConsts.OPTIMISED_MEMORY
            sum_field = avg_field
            max_field = avg_field
            min_field = avg_field
            value_field = avg_field
    elif scenario == KruizasterConsts.CPU_OPTIMISED:
        if metric in KruizasterConsts.CPU_METRICS and metric is not KruizasterConsts.CPU_THROTTLE:
            avg_field = KruizasterConsts.OPTIMISED_CPU
            sum_field = avg_field
            max_field = avg_field
            min_field = avg_field
            value_field = avg_field

        if metric in KruizasterConsts.MEMORY_METRICS:
            avg_field = Utils.generate_random_float(KruizasterConsts.MIN_AVG_MEMORY,
                                                    KruizasterConsts.MAX_AVG_MEMORY)
            sum_field = Utils.generate_random_int(KruizasterConsts.MIN_PODS,
                                                  KruizasterConsts.MAX_PODS) * avg_field

            max_field = Utils.generate_random_float(avg_field,
                                                    KruizasterConsts.MAX_MAX_MEMORY)

            min_field = Utils.generate_random_float(KruizasterConsts.MIN_MIN_MEMORY,
                                                    avg_field)

            value_field = Utils.generate_random_float(KruizasterConsts.MIN_MEMORY,
                                                      KruizasterConsts.MAX_MEMORY)

    elif scenario == KruizasterConsts.MEMORY_OPTIMISED:
        if metric in KruizasterConsts.CPU_METRICS:
            avg_field = Utils.generate_random_float(KruizasterConsts.MIN_AVG_CPU,
                                                    KruizasterConsts.MAX_AVG_CPU)
            sum_field = Utils.generate_random_int(KruizasterConsts.MIN_PODS,
                                                  KruizasterConsts.MAX_PODS) * avg_field

            max_field = Utils.generate_random_float(avg_field,
                                                    KruizasterConsts.MAX_MAX_CPU)

            min_field = Utils.generate_random_float(KruizasterConsts.MIN_MIN_CPU,
                                                    avg_field)

            value_field = Utils.generate_random_float(KruizasterConsts.MIN_CPU,
                                                      KruizasterConsts.MAX_CPU)
        if metric in KruizasterConsts.MEMORY_METRICS:
            avg_field = KruizasterConsts.OPTIMISED_MEMORY
            sum_field = avg_field
            max_field = avg_field
            min_field = avg_field
            value_field = avg_field

    elif scenario == KruizasterConsts.ONLY_CPU_REQUESTS_OPTIMISED:
        if metric == KruizasterConsts.CPU_LIMIT:
            avg_field = Utils.generate_random_float(KruizasterConsts.MIN_AVG_CPU,
                                                    KruizasterConsts.MAX_AVG_CPU)
            sum_field = Utils.generate_random_int(KruizasterConsts.MIN_PODS,
                                                  KruizasterConsts.MAX_PODS) * avg_field

            max_field = Utils.generate_random_float(avg_field,
                                                    KruizasterConsts.MAX_MAX_CPU)

            min_field = Utils.generate_random_float(KruizasterConsts.MIN_MIN_CPU,
                                                    avg_field)

            value_field = Utils.generate_random_float(KruizasterConsts.MIN_CPU,
                                                      KruizasterConsts.MAX_CPU)
        elif metric in KruizasterConsts.CPU_METRICS and metric is not KruizasterConsts.CPU_THROTTLE:
            avg_field = KruizasterConsts.OPTIMISED_CPU
            sum_field = avg_field
            max_field = avg_field
            min_field = avg_field
            value_field = avg_field

        if metric in KruizasterConsts.MEMORY_METRICS:
            avg_field = Utils.generate_random_float(KruizasterConsts.MIN_AVG_MEMORY,
                                                    KruizasterConsts.MAX_AVG_MEMORY)
            sum_field = Utils.generate_random_int(KruizasterConsts.MIN_PODS,
                                                  KruizasterConsts.MAX_PODS) * avg_field

            max_field = Utils.generate_random_float(avg_field,
                                                    KruizasterConsts.MAX_MAX_MEMORY)

            min_field = Utils.generate_random_float(KruizasterConsts.MIN_MIN_MEMORY,
                                                    avg_field)

            value_field = Utils.generate_random_float(KruizasterConsts.MIN_MEMORY,
                                                      KruizasterConsts.MAX_MEMORY)

    elif scenario == KruizasterConsts.ONLY_CPU_LIMITS_OPTIMISED:
        if metric == KruizasterConsts.CPU_REQUEST:
            avg_field = Utils.generate_random_float(KruizasterConsts.MIN_AVG_CPU,
                                                    KruizasterConsts.MAX_AVG_CPU)
            sum_field = Utils.generate_random_int(KruizasterConsts.MIN_PODS,
                                                  KruizasterConsts.MAX_PODS) * avg_field

            max_field = Utils.generate_random_float(avg_field,
                                                    KruizasterConsts.MAX_MAX_CPU)

            min_field = Utils.generate_random_float(KruizasterConsts.MIN_MIN_CPU,
                                                    avg_field)

            value_field = Utils.generate_random_float(KruizasterConsts.MIN_CPU,
                                                      KruizasterConsts.MAX_CPU)
        elif metric in KruizasterConsts.CPU_METRICS and metric is not KruizasterConsts.CPU_THROTTLE:
            avg_field = KruizasterConsts.OPTIMISED_CPU
            sum_field = avg_field
            max_field = avg_field
            min_field = avg_field
            value_field = avg_field

        if metric in KruizasterConsts.MEMORY_METRICS:
            avg_field = Utils.generate_random_float(KruizasterConsts.MIN_AVG_MEMORY,
                                                    KruizasterConsts.MAX_AVG_MEMORY)
            sum_field = Utils.generate_random_int(KruizasterConsts.MIN_PODS,
                                                  KruizasterConsts.MAX_PODS) * avg_field

            max_field = Utils.generate_random_float(avg_field,
                                                    KruizasterConsts.MAX_MAX_MEMORY)

            min_field = Utils.generate_random_float(KruizasterConsts.MIN_MIN_MEMORY,
                                                    avg_field)

            value_field = Utils.generate_random_float(KruizasterConsts.MIN_MEMORY,
                                                      KruizasterConsts.MAX_MEMORY)

    elif scenario == KruizasterConsts.ONLY_MEMORY_REQUESTS_OPTIMISED:
        if metric in KruizasterConsts.CPU_METRICS:
            avg_field = Utils.generate_random_float(KruizasterConsts.MIN_AVG_CPU,
                                                    KruizasterConsts.MAX_AVG_CPU)
            sum_field = Utils.generate_random_int(KruizasterConsts.MIN_PODS,
                                                  KruizasterConsts.MAX_PODS) * avg_field

            max_field = Utils.generate_random_float(avg_field,
                                                    KruizasterConsts.MAX_MAX_CPU)

            min_field = Utils.generate_random_float(KruizasterConsts.MIN_MIN_CPU,
                                                    avg_field)

            value_field = Utils.generate_random_float(KruizasterConsts.MIN_CPU,
                                                      KruizasterConsts.MAX_CPU)
        if metric in KruizasterConsts.MEMORY_METRICS:
            if metric == KruizasterConsts.MEMORY_LIMIT:
                avg_field = Utils.generate_random_float(KruizasterConsts.MIN_AVG_MEMORY,
                                                        KruizasterConsts.MAX_AVG_MEMORY)
                sum_field = Utils.generate_random_int(KruizasterConsts.MIN_PODS,
                                                      KruizasterConsts.MAX_PODS) * avg_field

                max_field = Utils.generate_random_float(avg_field,
                                                        KruizasterConsts.MAX_MAX_MEMORY)

                min_field = Utils.generate_random_float(KruizasterConsts.MIN_MIN_MEMORY,
                                                        avg_field)

                value_field = Utils.generate_random_float(KruizasterConsts.MIN_MEMORY,
                                                          KruizasterConsts.MAX_MEMORY)
            else:
                avg_field = KruizasterConsts.OPTIMISED_MEMORY
                sum_field = avg_field
                max_field = avg_field
                min_field = avg_field
                value_field = avg_field

    elif scenario == KruizasterConsts.ONLY_MEMORY_LIMITS_OPTIMISED:
        if metric in KruizasterConsts.CPU_METRICS:
            avg_field = Utils.generate_random_float(KruizasterConsts.MIN_AVG_CPU,
                                                    KruizasterConsts.MAX_AVG_CPU)
            sum_field = Utils.generate_random_int(KruizasterConsts.MIN_PODS,
                                                  KruizasterConsts.MAX_PODS) * avg_field

            max_field = Utils.generate_random_float(avg_field,
                                                    KruizasterConsts.MAX_MAX_CPU)

            min_field = Utils.generate_random_float(KruizasterConsts.MIN_MIN_CPU,
                                                    avg_field)

            value_field = Utils.generate_random_float(KruizasterConsts.MIN_CPU,
                                                      KruizasterConsts.MAX_CPU)
        if metric in KruizasterConsts.MEMORY_METRICS:
            if metric == KruizasterConsts.MEMORY_REQUEST:
                avg_field = Utils.generate_random_float(KruizasterConsts.MIN_AVG_MEMORY,
                                                        KruizasterConsts.MAX_AVG_MEMORY)
                sum_field = Utils.generate_random_int(KruizasterConsts.MIN_PODS,
                                                      KruizasterConsts.MAX_PODS) * avg_field

                max_field = Utils.generate_random_float(avg_field,
                                                        KruizasterConsts.MAX_MAX_MEMORY)

                min_field = Utils.generate_random_float(KruizasterConsts.MIN_MIN_MEMORY,
                                                        avg_field)

                value_field = Utils.generate_random_float(KruizasterConsts.MIN_MEMORY,
                                                          KruizasterConsts.MAX_MEMORY)
            else:
                avg_field = KruizasterConsts.OPTIMISED_MEMORY
                sum_field = avg_field
                max_field = avg_field
                min_field = avg_field
                value_field = avg_field




    values = {
        KruizasterConsts.VALUE: value_field,
        KruizasterConsts.SUM: sum_field,
        KruizasterConsts.AVG: avg_field,
        KruizasterConsts.MIN: min_field,
        KruizasterConsts.MAX: max_field
    }
    metric_data = Utils.get_metric_data_template(metric, values)

    return metric_data
