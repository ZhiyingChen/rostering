from .car import Car
from math import floor, ceil


class FactorSolver:
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
            raise BaseException("Serve number is larger than serve duration.")

        if (self.serve_dur % self.serve_num) != 0:
            raise BaseException("Serve num {} is not a factor of serve dur {}.".format(self.serve_num, self.serve_dur))

        self.max_gap = self.serve_dur / self.serve_num

        self.one_round_dur = self.upload_dur + self.leave_dur + self.serve_dur + \
                             self.return_dur + self.unpack_dur + self.prepare_dur

        if self.full_dur < self.one_round_dur:
            raise BaseException("Full dur {} is smaller than one round dur {}".format(self.full_dur, self.one_round_dur))

        self.continuous_round_num = floor(self.full_dur / self.one_round_dur)  # 保养之前可以连续跑几趟车
        self.interval = ceil(self.one_round_dur / self.max_gap) * self.max_gap # 同一辆车的最小发车间隔
        self.rest_slope = min(ceil(self.rest_dur / self.interval) * self.one_round_dur, self.full_dur)# 每两辆车之间需要错开的剩余总时间

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
                if self.rest_slope != 0:
                    if floor(last_dur / self.rest_slope) * self.rest_slope + self.rest_slope > self.full_dur:
                        last_dur = self.rest_slope
                    else:
                        last_dur = floor(last_dur / self.rest_slope) * self.rest_slope + self.rest_slope
                else:
                    last_dur = self.full_dur


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