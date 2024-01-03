from . import config as cg
from .factor_solver import FactorSolver
from math import sqrt
import pandas as pd
import sys
import copy

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
            fSolver = FactorSolver(stTime=self.start_time, edTime=self.end_time,
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
            fSolver = FactorSolver(stTime=self.start_time, edTime=self.end_time,
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
            fSolver = FactorSolver(stTime=self.start_time, edTime=self.end_time,
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
                if cg.actionName.serve in event.keys():
                    serve_dur = event[
                                    cg.actionName.serve] - car.upload_dur - car.leave_dur - car.return_dur - car.unpack_dur - car.prepare_dur
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

                elif cg.actionName.rest in event.keys():
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