import data_structure as ds
import config as cg
from time import time

if __name__ == '__main__':

    st = time()

    env = ds.factorSolver(stTime=cg.planHorizon.start_time, edTime=cg.planHorizon.end_time, serveNum=cg.serveInfo.serveNum,
            upload_dur=cg.CarSetting.upload_dur, unpack_dur=cg.CarSetting.unpack_dur, prepare_dur=cg.CarSetting.prepare_dur,
            leave_dur=cg.CarSetting.leave_dur, return_dur=cg.CarSetting.leave_dur, serve_dur=cg.CarSetting.serve_dur,
               rest_dur=cg.CarSetting.rest_dur, full_dur=cg.CarSetting.full_dur)
    env.dig_info()
    env.get_car_schedule()
    env.output()
    print("The validity of this schedule is {}".format(env.check_validity()))

    print(time() - st)