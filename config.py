
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
    end_time = 365*24

class CarSetting:
    upload_dur = 1
    unpack_dur = 1
    prepare_dur = 8
    leave_dur = 2
    return_dur = 2
    min_serve_dur = 6
    max_serve_dur = 6
    rest_dur = 40
    init_left_work_dur = 100
