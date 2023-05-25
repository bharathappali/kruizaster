from consts.cnario_consts import Constants as KruizasterConsts


class KruizasterSettings:
    KRUIZE_BASE_URL                                 = KruizasterConsts.ServiceInfo.Kruize.ServicePaths.BASE_URL
    KRUIZE_PORT                                     = KruizasterConsts.ServiceInfo.Kruize.ServicePaths.PORT

    KRUIZE_URL                                      = f"{KRUIZE_BASE_URL}:{KRUIZE_PORT}"
    KRUIZE_CREATE_EXP_URL                           = KRUIZE_URL + KruizasterConsts.ServiceInfo.Kruize.ServicePaths.CREATE_EXP_PATH
    KRUIZE_UPDATE_RESULTS_URL                       = KRUIZE_URL + KruizasterConsts.ServiceInfo.Kruize.ServicePaths.UPDATE_RESULTS_PATH
    KRUIZE_CREATE_PP_URL                            = KRUIZE_URL + KruizasterConsts.ServiceInfo.Kruize.ServicePaths.CREATE_PP_PATH
    KRUIZE_LIST_REC_URL                             = KRUIZE_URL + KruizasterConsts.ServiceInfo.Kruize.ServicePaths.LIST_REC_PATH