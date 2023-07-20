FILENAME = 'data.csv'

class planHorizon:
    start_time = 0
    end_time = 60*24

class serveInfo:
    serveNum = 7

class CarSetting:
    upload_dur = 1
    unpack_dur = 1
    prepare_dur = 8
    leave_dur = 2
    return_dur = 2
    serve_dur = 6
    rest_dur = 40
    full_dur = 200

class paramHeader:
    paramName = '参数名称'
    paramVal = '参数值'
    stTime = '计划开始时刻'
    edTime = '计划结束时刻'
    serveNum = '服务车辆'
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