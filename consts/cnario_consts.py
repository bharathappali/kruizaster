class Constants:
    VERSION                                         = "version"
    EXPERIMENT_NAME                                 = "experiment_name"
    CLUSTER_NAME                                    = "cluster_name"
    PERFORMANCE_PROFILE                             = "performance_profile"
    MODE                                            = "mode"
    TARGET_CLUSTER                                  = "target_cluster"
    KUBERNETES_OBJECTS                              = "kubernetes_objects"
    TYPE                                            = "type"
    NAME                                            = "name"
    NAMESPACE                                       = "namespace"
    CONTAINERS                                      = "containers"
    CONTAINER_IMAGE_NAME                            = "container_image_name"
    CONTAINER_NAME                                  = "container_name"
    TRIAL_SETTINGS                                  = "trial_settings"
    MEASUREMENT_DURATION                            = "measurement_duration"
    HISTORICAL_RESULTS                              = "historical_results"
    RECOMMENDATION_SETTINGS                         = "recommendation_settings"
    THRESHOLD                                       = "threshold"
    AUTO_GENERATE                                   = "auto_generate"
    CALENDAR_DURATION                               = "calendar_duration"
    START_TIMESTAMP                                 = "start_timestamp"
    END_TIMESTAMP                                   = "end_timestamp"
    METRICS                                         = "metrics"
    MIN                                             = "min"
    MAX                                             = "max"
    SUM                                             = "sum"
    AVG                                             = "avg"
    AGGREGATION_INFO                                = "aggregation_info"
    RESULTS                                         = "results"
    VALUE                                           = "value"
    FORMAT                                          = "format"
    INTERVAL_START_TIME                             = "interval_start_time"
    INTERVAL_END_TIME                               = "interval_end_time"
    TOTAL_ENTRIES                                   = "total_entries"
    NUM_DAYS                                        = "num_days"
    CURRENT_ENTRY                                   = "current_entry"
    COMPLETED_ENTRIES                               = "completed_entries"
    ENTRY_MIN_LIST                                  = "entry_min_list"
    RECOMMENDATIONS_GENERATED                       = "recommendations_generated"
    UPDATE_RESULTS_SUCCESS                          = "update_results_success"
    UPDATE_RESULTS_FAILED                           = "update_results_failed"
    MONITORING_START_TIME                           = "monitoring_start_time"
    MONITORING_END_TIME                             = "monitoring_end_time"

    # Constants for metric names
    CPU_REQUEST                                     = "cpuRequest"
    CPU_LIMIT                                       = "cpuLimit"
    CPU_USAGE                                       = "cpuUsage"
    CPU_THROTTLE                                    = "cpuThrottle"
    MEMORY_REQUEST                                  = "memoryRequest"
    MEMORY_LIMIT                                    = "memoryLimit"
    MEMORY_USAGE                                    = "memoryUsage"
    MEMORY_RSS                                      = "memoryRSS"

    CPU_METRICS                     = [
        CPU_USAGE,
        CPU_LIMIT,
        CPU_REQUEST,
        CPU_THROTTLE,
    ]

    MEMORY_METRICS                  = [
        MEMORY_USAGE,
        MEMORY_LIMIT,
        MEMORY_REQUEST,
        MEMORY_RSS
    ]

    ALL_METRICS                     = CPU_METRICS + MEMORY_METRICS

    # Disaster scenarios
    DEFAULT                                         = "default"
    NO_DISASTER                                     = "no_disaster"
    ZERO_CPUS_RECORDS                               = "zero_cpu_recording"
    ZERO_MEMORY_RECORDS                             = "zero_memory_recording"
    IDLE_CPU                                        = "cpu_idle"

    SCENARIO                                        = "scenario"

    SCENARIOS                   = [
        DEFAULT,
        NO_DISASTER,
        ZERO_CPUS_RECORDS,
        ZERO_MEMORY_RECORDS,
        IDLE_CPU
    ]

    ADJECTIVES                  = [
        'adorable',
        'amazing',
        'beautiful',
        'breathtaking',
        'brilliant',
        'charming',
        'dazzling',
        'delightful',
        'elegant',
        'exquisite',
        'fascinating',
        'fantastic',
        'glorious',
        'gorgeous',
        'graceful',
        'harmonious',
        'hilarious',
        'incredible',
        'inspiring',
        'jubilant',
        'joyful',
        'kind',
        'lovely',
        'magnanimous',
        'magnificent',
        'noble',
        'nurturing',
        'optimistic',
        'outstanding',
        'passionate',
        'playful',
        'quirky',
        'radiant',
        'resilient',
        'sensational',
        'serendipitous',
        'serene',
        'terrific',
        'thrilling',
        'unique',
        'uplifting',
        'vivacious',
        'whimsical',
        'witty',
        'xenial',
        'youthful',
        'zealous'
    ]

    NAMES                   = [
        'bharath',
        'bhanvi',
        'chandrakala',
        'dinakar',
        'kusuma',
        'prathamesh',
        'rashmi',
        'saad',
        'shreya',
        'vinay'
    ]

    # Interval Duration Units
    SECONDS                                         = "seconds"
    MINUTES                                         = "minutes"
    HOURS                                           = "hours"

    INTERVAL_DURATION_UNITS                     = [
        MINUTES,
        HOURS
    ]
    # Duration opts
    MINS_5                                          = "5 " + MINUTES.capitalize()
    MINS_10                                         = "10 " + MINUTES.capitalize()
    MINS_15                                         = "15 " + MINUTES.capitalize()
    MINS_30                                         = "30 " + MINUTES.capitalize()
    MINS_45                                         = "45 " + MINUTES.capitalize()
    HOUR_1                                          = "1 " + HOURS.capitalize()

    INTERVAL_DURATION_OPTS                  = [
        MINS_15,
        MINS_30,
        MINS_45,
        HOUR_1
    ]

    STANDARD_DATE_TIME_FORMAT                       = "%Y-%m-%dT%H:%M:%S.%f%Z"
    KRUIZE_PARTIAL_FORMAT                           = "%Y-%m-%dT%H:%M:%S"
    Z_FORMAT                                        = "Z"

    METADATA                                        = "metadata"
    DATA                                            = "data"
    STATUS                                          = "status"
    TOTAL_DURATION                                  = "total_duration"

    CREATING                                        = "creating"
    UPLOADING                                       = "uploading"
    COMPLETED                                       = "completed"

    KRUIZASTER_EXP_DATA                             = "kruizaster_exp_data"
    KRUIZASTER_EXP_RESULTS                          = "kruizaster_exp_results"
    KRUIZASTER_EXP_RECS                             = "kruizaster_exp_recs"

    ZERO_VAL                                        = 0.00
    MIN_CPU                                         = 0.01
    MAX_CPU                                         = 4.00
    MIN_MIN_CPU                                     = MIN_CPU
    MIN_AVG_CPU                                     = 0.50
    MAX_AVG_CPU                                     = 3.50
    MIN_MAX_CPU                                     = 2.00
    MAX_MAX_CPU                                     = MAX_CPU
    IDLE_CPU_MIN                                    = 0.00001
    IDLE_CPU_MAX                                    = 0.0001

    MIN_MEMORY                                      = 50.00
    MAX_MEMORY                                      = 999.00
    MIN_MIN_MEMORY                                  = MIN_MEMORY
    MIN_AVG_MEMORY                                  = 200.00
    MAX_AVG_MEMORY                                  = 850.00
    MIN_MAX_MEMORY                                  = 500.00
    MAX_MAX_MEMORY                                  = MAX_MEMORY

    MAX_PODS                                        = 1
    MIN_PODS                                        = 1

    AVAILABLE_FUNCS                                 = "available_functions"
    ENTRY_ID                                        = "entry_id"
    DAY                                             = "day"
    DAY_ENTRY_ID                                    = "day_entry_id"

    DEPLOYMENT                                      = "deployment"
    SAMPLE_DEPLOYMENT                               = "my-sample-deployment"
    SAMPLE_CONTAINER                                = "my-sample-container"
    SAMPLE_IMAGE                                    = "my-sample-image"

    # Experiment statuses
    CREATING_EXPERIMENT                             = "Creating Experiment"
    GENERATING_RESULTS                              = "Generating Results"
    UPLOADING_RESULTS                               = "Uploading Results"
    OBTAINED_RECOMMENDATIONS                        = "Obtained Recommendations"

    # Url consts
    URL_PARAM_SPECIFIER                             = "?"
    URL_PARAM_ADDER                                 = "&"
    URL_PARAM_VALUE_EQUAL                           = "="

    MESSAGE                                         = "message"
    UTF_8                                           = "utf-8"

    # Messages
    BACK_TO_HOME                                    = "Back To Home"
    TRY_AGAIN                                       = "Try Again"

    # Websocket status
    UPDATE_RESULTS_STATUS                           = "update_results_status"
    RECOMMENDATION_STATUS                           = "recommendations_status"

    ERROR                                           = "ERROR"
    HTTP_CODE                                       = "httpcode"

    CONFIG                                          = "config"
    REQUESTS                                        = "requests"
    LIMITS                                          = "limits"
    AMOUNT                                          = "amount"
    CPU                                             = "cpu"
    MEMORY                                          = "memory"
    RECOMMENDATIONS                                 = "recommendations"

    VARIATION                                       = "variation"
    DURATION_BASED                                  = "duration_based"
    SHORT_TERM                                      = "short_term"
    MEDIUM_TERM                                     = "medium_term"
    LONG_TERM                                       = "long_term"




    class ServiceInfo:
        class Kruize:
            class ServicePaths:
                BASE_URL                                = "http://192.168.49.2"
                PORT                                    = 31869
                CREATE_EXP_PATH                         = "/createExperiment"
                UPDATE_RESULTS_PATH                     = "/updateResults"
                CREATE_PP_PATH                          = "/createPerformanceProfile"
                LIST_REC_PATH                           = "/listRecommendations"
        class Kruizaster:
            class ServicePaths:
                ROOT                                    = "/"
                CREATE_DISASTER                         = "/create_disaster"
                TEST                                    = "/test"
                UPDATES_SOCKET                          = "/update_socket/{experiment_name}"
                VIEW_EXPERIMENT                         = "/view/{experiment_name}/"
                VIEW_EXPERIMENT_RESULTS                 = "/view/{experiment_name}/result/{interval_end_time}"
                LIST_EXPERIMENTS                        = "/list_experiments"


