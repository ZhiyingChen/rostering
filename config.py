import pandas as pd
class paramHeader:
    paramName = '参数名称'
    paramVal = '参数值'
    stTime = '计划开始时刻'
    edTime = '计划结束时刻'
    packDur = '装货时间'
    unpackDur = '卸货时间'
    prepareDur = '备货时间'
    goDur = '去程时间'
    returnDur = '返程时间'
    serveDur = '服务时间'
    restDur = '维修时间'
    maxWorkDur = '最大工作时间'

class Sign:
    upload = '0'
    unpack = '4'
    prepare = '5'
    leave = '1'
    back = '3'
    serve = '2'
    fix = '6'
    spare = '7'


class planHorizon:
    start_time = 0
    end_time = 90*24

class CarSetting:
    upload_dur = 1
    unpack_dur = 1
    prepare_dur = 8
    leave_dur = 2
    return_dur = 2
    max_serve_dur = 6
    rest_dur = 40
    init_left_work_dur = 100

def read_config():
    filename = 'data.csv'
    df = pd.read_csv(filename, dtype={paramHeader.paramName: str,  paramHeader.paramVal: int})
    config_dict = df.set_index(paramHeader.paramName)[paramHeader.paramVal].to_dict()

    planHorizon.start_time = config_dict[paramHeader.stTime]
    planHorizon.end_time = config_dict[paramHeader.edTime]
    CarSetting.upload_dur = config_dict[paramHeader.packDur]
    CarSetting.unpack_dur = config_dict[paramHeader.unpackDur]
    CarSetting.prepare_dur = config_dict[paramHeader.prepareDur]
    CarSetting.leave_dur = config_dict[paramHeader.goDur]
    CarSetting.return_dur = config_dict[paramHeader.returnDur]
    CarSetting.max_serve_dur = config_dict[paramHeader.serveDur]
    CarSetting.rest_dur = config_dict[paramHeader.restDur]
    CarSetting.init_left_work_dur = config_dict[paramHeader.maxWorkDur]