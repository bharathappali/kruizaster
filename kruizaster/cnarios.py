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

            max_field = Utils.generate_random_float(KruizasterConsts.MIN_MAX_CPU,
                                                    KruizasterConsts.MAX_MAX_CPU)

            min_field = Utils.generate_random_float(KruizasterConsts.MIN_MIN_CPU,
                                                    KruizasterConsts.MIN_AVG_CPU)

            value_field = Utils.generate_random_float(KruizasterConsts.MIN_CPU,
                                                      KruizasterConsts.MAX_CPU)
        # Generate Memory Fields
        elif metric in KruizasterConsts.MEMORY_METRICS:
            avg_field = Utils.generate_random_float(KruizasterConsts.MIN_AVG_MEMORY,
                                                    KruizasterConsts.MAX_AVG_MEMORY)
            sum_field = Utils.generate_random_int(KruizasterConsts.MIN_PODS,
                                                  KruizasterConsts.MAX_PODS) * avg_field

            max_field = Utils.generate_random_float(KruizasterConsts.MIN_MAX_MEMORY,
                                                    KruizasterConsts.MAX_MAX_MEMORY)

            min_field = Utils.generate_random_float(KruizasterConsts.MIN_MIN_MEMORY,
                                                    KruizasterConsts.MIN_AVG_MEMORY)

            value_field = Utils.generate_random_float(KruizasterConsts.MIN_MEMORY,
                                                      KruizasterConsts.MAX_MEMORY)
    # Generate fields for Zero cpu values Scenario
    elif scenario == KruizasterConsts.ZERO_CPUS_RECORDS:
        if metric in KruizasterConsts.MEMORY_METRICS:
            avg_field = Utils.generate_random_float(KruizasterConsts.MIN_AVG_MEMORY,
                                                    KruizasterConsts.MAX_AVG_MEMORY)
            sum_field = Utils.generate_random_int(KruizasterConsts.MIN_PODS,
                                                  KruizasterConsts.MAX_PODS) * avg_field

            max_field = Utils.generate_random_float(KruizasterConsts.MIN_MAX_MEMORY,
                                                    KruizasterConsts.MAX_MAX_MEMORY)

            min_field = Utils.generate_random_float(KruizasterConsts.MIN_MIN_MEMORY,
                                                    KruizasterConsts.MIN_AVG_MEMORY)

            value_field = Utils.generate_random_float(KruizasterConsts.MIN_MEMORY,
                                                      KruizasterConsts.MAX_MEMORY)
    # Generate fields for Zero memory Scenario
    elif scenario == KruizasterConsts.ZERO_MEMORY_RECORDS:
        if metric in KruizasterConsts.CPU_METRICS:
            avg_field = Utils.generate_random_float(KruizasterConsts.MIN_AVG_CPU,
                                                    KruizasterConsts.MAX_AVG_CPU)
            sum_field = Utils.generate_random_int(KruizasterConsts.MIN_PODS,
                                                  KruizasterConsts.MAX_PODS) * avg_field

            max_field = Utils.generate_random_float(KruizasterConsts.MIN_MAX_CPU,
                                                    KruizasterConsts.MAX_MAX_CPU)

            min_field = Utils.generate_random_float(KruizasterConsts.MIN_MIN_CPU,
                                                    KruizasterConsts.MIN_AVG_CPU)

            value_field = Utils.generate_random_float(KruizasterConsts.MIN_CPU,
                                                      KruizasterConsts.MAX_CPU)

    values = {
        KruizasterConsts.VALUE: value_field,
        KruizasterConsts.SUM: sum_field,
        KruizasterConsts.AVG: avg_field,
        KruizasterConsts.MIN: min_field,
        KruizasterConsts.MAX: max_field
    }
    metric_data = Utils.get_metric_data_template(metric, values)

    return metric_data
