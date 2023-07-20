from . import config as cg
from math import floor, ceil, sqrt
import pandas as pd
import sys
import copy

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

    def get_min_car_num(self):
        self.dig_info()
        self.get_car_schedule()
        return len(self.car_dict)

class Solver:
    def __init__(self, stTime, edTime, serveNum,
                 upload_dur, unpack_dur, prepare_dur, leave_dur, return_dur, serve_dur, rest_dur, full_dur):
        self.file = cg.FILENAME
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

        self.factors = list()
        self.factor_car_num = dict()
        self.factor_car_dict = dict()
        self.factor_combination = dict()

        self.car_dict = dict()
        self.schedule_df = dict()
        self.serve_distribution = dict()

    def read_config(self):

        df = pd.read_csv(self.file, dtype={cg.paramHeader.paramName: str, cg.paramHeader.paramVal: int})
        config_dict = df.set_index(cg.paramHeader.paramName)[cg.paramHeader.paramVal].to_dict()

        self.start_time = config_dict[cg.paramHeader.stTime]
        self.end_time = config_dict[cg.paramHeader.edTime]

        self.serve_num = config_dict[cg.paramHeader.serveNum]

        self.upload_dur = config_dict[cg.paramHeader.packDur]
        self.unpack_dur = config_dict[cg.paramHeader.unpackDur]
        self.prepare_dur = config_dict[cg.paramHeader.prepareDur]
        self.leave_dur = config_dict[cg.paramHeader.goDur]
        self.return_dur = config_dict[cg.paramHeader.returnDur]
        self.serve_dur = config_dict[cg.paramHeader.serveDur]
        self.rest_dur = config_dict[cg.paramHeader.restDur]

        self.full_dur = config_dict[cg.paramHeader.maxWorkDur]

    def find_all_factors(self):
        factors = []
        for_times = int(sqrt(self.serve_dur))
        for i in range(1, for_times + 1):
            if self.serve_dur % i == 0:
                factors.append(i)
                t = int(self.serve_dur / i)
                if not t == i:
                    factors.append(t)

        factors = sorted(factors)
        return factors

    def get_factor_car_num(self):
        factor_car_num = {}
        factor_car_dict = {}
        factors = [f for f in self.factors if f <= self.serve_num]
        for f in factors:
            fSolver = factorSolver(stTime=self.start_time, edTime=self.end_time,
                                  serveNum=f,
                                  upload_dur=self.upload_dur, unpack_dur=self.unpack_dur,
                                  prepare_dur=self.prepare_dur,
                                  leave_dur=self.leave_dur, return_dur=self.leave_dur,
                                  serve_dur=self.serve_dur,
                                  rest_dur=self.rest_dur, full_dur=self.full_dur)
            min_car = fSolver.get_min_car_num()
            factor_car_num.update({f: min_car})
            factor_car_dict.update({f: fSolver.car_dict})
        return factor_car_num, factor_car_dict

    def find_factor_combination(self):
        factors = list(self.factor_car_num.keys())
        factors = sorted([f for f in factors if f <= self.serve_num], reverse=True)

        factor_combination = dict()

        left = self.serve_num
        for f in factors:
            if left == 0:
                break
            times = int(left / f)

            factor_combination[f] = times
            left -= times * f

        factor_multiples = sum(k*v for k, v in factor_combination.items())
        if factor_multiples != self.serve_num:
            sys.exit(-1)
            print("Something went wrong with factor combination.")

        return factor_combination

    def generate_min_car_num(self):
        if self.serve_dur > self.serve_num and (self.serve_dur % self.serve_num) == 0:
            fSolver = factorSolver(stTime=self.start_time, edTime=self.end_time,
                                   serveNum=self.serve_num,
                                   upload_dur=self.upload_dur, unpack_dur=self.unpack_dur,
                                   prepare_dur=self.prepare_dur,
                                   leave_dur=self.leave_dur, return_dur=self.leave_dur,
                                   serve_dur=self.serve_dur,
                                   rest_dur=self.rest_dur, full_dur=self.full_dur)
            min_car = fSolver.get_min_car_num()
            return min_car

        self.factors = self.find_all_factors()
        self.factor_car_num, self.factor_car_dict = self.get_factor_car_num()
        self.factor_combination = self.find_factor_combination()

        min_car = 0
        for f, times in self.factor_combination.items():
            min_car += times * self.factor_car_num[f]
        return min_car

    def generate_car_schedule(self):
        if self.serve_dur > self.serve_num and (self.serve_dur % self.serve_num) == 0:
            fSolver = factorSolver(stTime=self.start_time, edTime=self.end_time,
                                  serveNum=self.serve_num,
                                  upload_dur=self.upload_dur, unpack_dur=self.unpack_dur,
                                  prepare_dur=self.prepare_dur,
                                  leave_dur=self.leave_dur, return_dur=self.leave_dur,
                                  serve_dur=self.serve_dur,
                                  rest_dur=self.rest_dur, full_dur=self.full_dur)
            min_car = fSolver.get_min_car_num()
            self.car_dict = fSolver.car_dict
            return

        self.factors = self.find_all_factors()
        self.factor_car_num, self.factor_car_dict = self.get_factor_car_num()
        self.factor_combination = self.find_factor_combination()

        c_id = 0
        car_dict = {}
        for f, times in self.factor_combination.items():
            if times < 1:
                continue
            f_car_dict = copy.deepcopy(self.factor_car_dict[f])
            new_dict = {c_id + k + i * len(f_car_dict): v for i in range(times) for k, v in f_car_dict.items()}
            c_id += len(new_dict)
            car_dict.update(new_dict)

        self.car_dict = car_dict

    def generate_car_distribution(self):

        record_dict = {}
        for c_id, car in self.car_dict.items():
            record = {k: '' for k in range(self.start_time, self.end_time + 1)}
            for t, event in car.schedule.items():
                if 'serve' in event.keys():
                    serve_dur = event[
                                    'serve'] - car.upload_dur - car.leave_dur - car.return_dur - car.unpack_dur - car.prepare_dur
                    curr_t = t

                    for i in range(car.upload_dur):
                        record[curr_t] = cg.Sign.upload
                        curr_t += 1

                    for i in range(car.leave_dur):
                        record[curr_t] = cg.Sign.leave
                        curr_t += 1

                    for i in range(serve_dur):
                        record[curr_t] = cg.Sign.serve
                        curr_t += 1

                    for i in range(car.return_dur):
                        record[curr_t] = cg.Sign.back
                        curr_t += 1
                    for i in range(car.unpack_dur):
                        record[curr_t] = cg.Sign.unpack
                        curr_t += 1
                    for i in range(car.prepare_dur):
                        record[curr_t] = cg.Sign.prepare
                        curr_t += 1

                elif 'rest' in event.keys():
                    curr_t = t
                    for i in range(car.rest_dur):
                        record[curr_t] = cg.Sign.fix
                        curr_t += 1

            record_dict[c_id] = record

        out_df = pd.DataFrame(record_dict, dtype=object)
        out_df.replace('', cg.Sign.spare, inplace=True)
        out_df = out_df.loc[self.start_time:self.end_time]
        out_df.set_axis(list(range(1, out_df.shape[1] + 1)), axis=1, inplace=True)

        self.schedule_df = out_df

        self.serve_distribution = dict()
        for hour, car_status in self.schedule_df.iterrows():
            status_lt = list(car_status)
            serve_num = status_lt.count(cg.Sign.serve)
            self.serve_distribution[hour] = serve_num

    def output_df(self):
        self.schedule_df.to_csv('output.csv')

    def check_validity4dist(self):
        lst = list(self.serve_distribution.values())
        judge_lst = [x >= self.serve_num for x in lst]

        try:
            first_true = judge_lst .index(True)
            return len(judge_lst) - first_true == judge_lst.count(True)
        except ValueError:
            return False



