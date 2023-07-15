from math import floor, ceil
from config import CarSetting, planHorizon, serveInfo, Sign, paramHeader
import pandas as pd

class Car:
    def __init__(self, id, t0, full_dur, left_dur,
                 upload_dur, leave_dur, serve_dur, return_dur,unpack_dur, prepare_dur, rest_dur):

        self.id = id
        self.earliest_avl_time = t0

        self.left_dur = left_dur
        self.full_dur = full_dur

        self.upload_dur = upload_dur
        self.leave_dur = leave_dur
        self.serve_dur = serve_dur
        self.return_dur = return_dur
        self.unpack_dur = unpack_dur
        self.prepare_dur = prepare_dur
        self.rest_dur = rest_dur

        self.schedule = {}

    def is_able_serve(self, curr_t):
        if self.earliest_avl_time <= curr_t and \
                (self.upload_dur + self.leave_dur + self.serve_dur + self.return_dur + self.unpack_dur + self.prepare_dur) <= self.left_dur:
            return True
        return False

    def serve_and_update(self, curr_t):
        self.schedule[curr_t] = {'serve': (self.upload_dur + self.leave_dur + self.serve_dur + self.return_dur + self.unpack_dur + self.prepare_dur)}
        self.left_dur = self.left_dur - (self.upload_dur + self.leave_dur + self.serve_dur + self.return_dur + self.unpack_dur + self.prepare_dur)
        self.earliest_avl_time = curr_t + (self.upload_dur + self.leave_dur + self.serve_dur + self.return_dur + self.unpack_dur + self.prepare_dur)

        if not self.is_able_serve(self.earliest_avl_time):
            self.rest_and_update(self.earliest_avl_time)

    def rest_and_update(self, curr_t):
        self.schedule[curr_t] = {'rest': self.rest_dur}
        self.earliest_avl_time = curr_t + self.rest_dur
        self.left_dur = self.full_dur

class Env:
    def __init__(self):
        self.file = 'data.csv'
        self.start_time = planHorizon.start_time
        self.end_time = planHorizon.end_time

        self.serve_num = serveInfo.serveNum

        self.upload_dur = CarSetting.upload_dur
        self.unpack_dur = CarSetting.unpack_dur
        self.prepare_dur = CarSetting.prepare_dur
        self.leave_dur = CarSetting.leave_dur
        self.return_dur = CarSetting.return_dur
        self.serve_dur = CarSetting.serve_dur
        self.rest_dur = CarSetting.rest_dur
        self.full_dur = CarSetting.full_dur

        self.car_dict = {}


    def read_config(self):

        df = pd.read_csv(self.file, dtype={paramHeader.paramName: str, paramHeader.paramVal: int})
        config_dict = df.set_index(paramHeader.paramName)[paramHeader.paramVal].to_dict()

        self.start_time = config_dict[paramHeader.stTime]
        self.end_time = config_dict[paramHeader.edTime]

        self.serve_num = config_dict[paramHeader.serveNum]
        self.max_gap = ceil(self.serve_dur / self.serve_num)

        self.upload_dur = config_dict[paramHeader.packDur]
        self.unpack_dur = config_dict[paramHeader.unpackDur]
        self.prepare_dur = config_dict[paramHeader.prepareDur]
        self.leave_dur = config_dict[paramHeader.goDur]
        self.return_dur = config_dict[paramHeader.returnDur]
        self.serve_dur = config_dict[paramHeader.serveDur]
        self.rest_dur = config_dict[paramHeader.restDur]

        self.full_dur = config_dict[paramHeader.maxWorkDur]

    def dig_info(self):
        self.one_round_dur = self.upload_dur + self.leave_dur + self.serve_dur + \
                             self.return_dur + self.unpack_dur + self.prepare_dur
        self.continuous_round_num = floor(self.full_dur / self.one_round_dur)  # 保养之前可以连续跑几趟车
        self.interval = ceil(self.one_round_dur / self.serve_dur) * self.serve_dur  # 同一辆车的最小发车间隔
        self.rest_slope = ceil(self.rest_dur / self.interval) * self.one_round_dur  # 每两辆车之间需要错开的剩余总时间

        self.max_gap = ceil(self.serve_dur / self.serve_num)

    def whether_car_avl(self, t):
        for c_id, car in self.car_dict.items():
            if car.is_able_serve(t):
                return True
        return False

    def get_avl_car(self, t):
        # 选出 left dur 最小的car
        best_c = None
        min_left_dur = float('inf')
        for c_id, car in self.car_dict.items():
            if car.is_able_serve(t):
                if car.left_dur <= min_left_dur:
                    best_c = c_id
                    min_left_dur = car.left_dur
        return best_c

    def get_car_schedule(self):
        t = self.start_time
        id = 1
        last_dur = self.rest_slope
        while t <= self.end_time:
            avl = self.whether_car_avl(t)
            if avl:
                c_id = self.get_avl_car(t)
                car = self.car_dict[c_id]
                last_dur = car.left_dur
                car.serve_and_update(t)
            else:
                if last_dur + self.rest_slope > self.full_dur:
                    last_dur = (last_dur + self.rest_slope) % self.full_dur
                else:
                    last_dur += self.rest_slope

                new_car = Car(id=id, t0=t, full_dur=self.full_dur, left_dur=last_dur,
                              upload_dur=self.upload_dur, leave_dur=self.leave_dur,
                              serve_dur=self.serve_dur,
                              return_dur=self.return_dur, unpack_dur=self.unpack_dur,
                              prepare_dur=self.prepare_dur,
                              rest_dur=self.rest_dur)  # 初始化一辆新车

                new_car.serve_and_update(t)
                self.car_dict[new_car.id] = new_car
                id += 1

            t += self.max_gap

    def output(self):

        record_dict = {}
        for c_id, car in self.car_dict.items():
            record = {k: '' for k in range(self.start_time, self.end_time + 1)}
            for t, event in car.schedule.items():
                if 'serve' in event.keys():
                    serve_dur = event[
                                    'serve'] - car.upload_dur - car.leave_dur - car.return_dur - car.unpack_dur - car.prepare_dur
                    curr_t = t

                    for i in range(car.upload_dur):
                        record[curr_t] = Sign.upload
                        curr_t += 1

                    for i in range(car.leave_dur):
                        record[curr_t] = Sign.leave
                        curr_t += 1

                    for i in range(serve_dur):
                        record[curr_t] = Sign.serve
                        curr_t += 1

                    for i in range(car.return_dur):
                        record[curr_t] = Sign.back
                        curr_t += 1
                    for i in range(car.unpack_dur):
                        record[curr_t] = Sign.unpack
                        curr_t += 1
                    for i in range(car.prepare_dur):
                        record[curr_t] = Sign.prepare
                        curr_t += 1

                elif 'rest' in event.keys():
                    curr_t = t
                    for i in range(car.rest_dur):
                        record[curr_t] = Sign.fix
                        curr_t += 1

            record_dict[c_id] = record

        out_df = pd.DataFrame(record_dict, dtype=object)
        out_df.replace('', Sign.spare, inplace=True)
        out_df = out_df.loc[self.start_time:self.end_time]
        out_df.set_axis(list(range(1, out_df.shape[1] + 1)), axis=1, inplace=True)
        out_df.to_csv('output.csv')