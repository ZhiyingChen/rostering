from math import floor, ceil
from config import CarSetting, planHorizon, serveInfo, Sign, paramHeader
import pandas as pd
import sys

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

    def __repr__(self):
        return "Car(id={}, avl={}, left={})".format(self.id, self.earliest_avl_time, self.left_dur)

class factorSolver:
    def __init__(self, stTime, edTime, serveNum,
                 upload_dur, unpack_dur, prepare_dur, leave_dur, return_dur, serve_dur, rest_dur, full_dur):
        self.start_time = stTime
        self.end_time = edTime

        self.serve_num = serveNum

        self.upload_dur = upload_dur
        self.unpack_dur = unpack_dur
        self.prepare_dur = prepare_dur
        self.leave_dur = leave_dur
        self.return_dur = return_dur
        self.serve_dur = serve_dur
        self.rest_dur = rest_dur
        self.full_dur = full_dur

        self.car_dict = {}

    def dig_info(self):
        if self.serve_num > self.serve_dur:
            print("Serve number is larger than serve duration.")
            sys.exit(-1)
        if (self.serve_dur % self.serve_num) != 0:
            print("Serve num {} is not a factor of serve dur {}.".format(self.serve_num, self.serve_dur))
            sys.exit(-1)

        self.max_gap = self.serve_dur / self.serve_num

        self.one_round_dur = self.upload_dur + self.leave_dur + self.serve_dur + \
                             self.return_dur + self.unpack_dur + self.prepare_dur
        self.continuous_round_num = floor(self.full_dur / self.one_round_dur)  # 保养之前可以连续跑几趟车
        self.interval = ceil(self.one_round_dur / self.serve_dur) * self.serve_dur  # 同一辆车的最小发车间隔
        self.rest_slope = ceil(self.rest_dur / self.interval) * self.one_round_dur  # 每两辆车之间需要错开的剩余总时间


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
        self.schedule_df = out_df

        self.serve_distribution = dict()
        for hour, car_status in self.schedule_df.iterrows():
            status_lt = list(car_status)
            serve_num = status_lt.count(Sign.serve)
            self.serve_distribution[hour] = serve_num

    def check_validity(self):
        lst = list(self.serve_distribution.values())
        judge_lst = [x >= self.serve_num for x in lst]

        try:
            first_true = judge_lst .index(True)
            return len(judge_lst) - first_true == judge_lst.count(True)
        except ValueError:
            return False


class Solver:
    def __init__(self, stTime, edTime, serveNum,
                 upload_dur, unpack_dur, prepare_dur, leave_dur, return_dur, serve_dur, rest_dur, full_dur):

        self.start_time = stTime
        self.end_time = edTime

        self.serve_num = serveNum

        self.upload_dur = upload_dur
        self.unpack_dur = unpack_dur
        self.prepare_dur = prepare_dur
        self.leave_dur = leave_dur
        self.return_dur = return_dur
        self.serve_dur = serve_dur
        self.rest_dur = rest_dur
        self.full_dur = full_dur

        self.factors = set()

        self.car_dict = {}

    def find_all_factors(self):
        pass



