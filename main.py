from singleRoster.solver import Solver
import singleRoster.config as cg
from time import time

if __name__ == '__main__':

    st = time()

    env = Solver(stTime=cg.planHorizon.start_time, edTime=cg.planHorizon.end_time, serveNum=cg.serveInfo.serveNum,
            upload_dur=cg.CarSetting.upload_dur, unpack_dur=cg.CarSetting.unpack_dur, prepare_dur=cg.CarSetting.prepare_dur,
            leave_dur=cg.CarSetting.leave_dur, return_dur=cg.CarSetting.leave_dur, serve_dur=cg.CarSetting.serve_dur,
               rest_dur=cg.CarSetting.rest_dur, full_dur=cg.CarSetting.full_dur)

    env.read_config()
    env.generate_car_schedule()
    env.generate_car_distribution()
    print("The validity of this schedule is {}".format(env.check_validity4dist()))

    result_df = env.output_df()
    print(time() - st)