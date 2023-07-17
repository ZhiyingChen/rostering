from math import floor, ceil
from config import Sign
import pandas as pd
import logging

class Plane:
    def __init__(self, id, t0, full_dur, left_dur,
                 upload_dur, leave_dur, serve_dur, return_dur, unpack_dur, rest_dur):

        self.id = id
        self.earliest_avl_time = t0

        self.left_dur = left_dur
        self.full_dur = full_dur

        self.upload_dur = upload_dur
        self.leave_dur = leave_dur
        self.serve_dur = serve_dur
        self.return_dur = return_dur
        self.unpack_dur = unpack_dur
        self.rest_dur = rest_dur

        self.schedule = {}

    def is_able_serve(self, curr_t):
        if self.earliest_avl_time <= curr_t and \
                (self.upload_dur + self.leave_dur + self.serve_dur + self.return_dur + self.unpack_dur) <= self.left_dur:
            return True
        return False

    def serve_and_update(self, curr_t):
        self.schedule[curr_t] = {'serve': (self.upload_dur + self.leave_dur + self.serve_dur + self.return_dur + self.unpack_dur)}
        self.left_dur = self.left_dur - (self.upload_dur + self.leave_dur + self.serve_dur + self.return_dur + self.unpack_dur)
        self.earliest_avl_time = curr_t + (self.upload_dur + self.leave_dur + self.serve_dur + self.return_dur + self.unpack_dur)

        if not self.is_able_serve(self.earliest_avl_time):
            self.rest_and_update(self.earliest_avl_time)

    def rest_and_update(self, curr_t):
        self.schedule[curr_t] = {'rest': self.rest_dur}
        self.earliest_avl_time = curr_t + self.rest_dur
        self.left_dur = self.full_dur

    def __repr__(self):
        return "Plane(id={}, avl={}, left={})".format(self.id, self.earliest_avl_time, self.left_dur)

class singlePlaneEnv:
    def __init__(self, start_time, end_time, serve_num,
                 upload_dur, unpack_dur, leave_dur, return_dur, serve_dur, rest_dur, full_dur):
        self.start_time = start_time
        self.end_time = end_time

        self.serve_num = serve_num

        self.upload_dur = upload_dur
        self.unpack_dur = unpack_dur
        self.leave_dur = leave_dur
        self.return_dur = return_dur
        self.serve_dur = serve_dur
        self.rest_dur = rest_dur
        self.full_dur = full_dur

        self.plane_dict = {}

    def dig_info(self):
        self.one_round_dur = self.upload_dur + self.leave_dur + self.serve_dur + \
                             self.return_dur + self.unpack_dur
        self.continuous_round_num = floor(self.full_dur / self.one_round_dur)  # 保养之前可以连续跑几趟车
        self.interval = ceil(self.one_round_dur / self.serve_dur) * self.serve_dur  # 同一辆车的最小发车间隔
        self.rest_slope = ceil(self.rest_dur / self.interval) * self.one_round_dur  # 每两辆车之间需要错开的剩余总时间

        self.max_gap = ceil(self.serve_dur / self.serve_num)

    def whether_plane_avl(self, t):
        for c_id, plane in self.plane_dict.items():
            if plane.is_able_serve(t):
                return True
        return False

    def get_avl_plane(self, t):
        # 选出 left dur 最小的plane
        best_c = None
        min_left_dur = float('inf')
        for c_id, plane in self.plane_dict.items():
            if plane.is_able_serve(t):
                if plane.left_dur <= min_left_dur:
                    best_c = c_id
                    min_left_dur = plane.left_dur
        return best_c

    def get_plane_schedule(self):
        t = self.start_time
        id = 1
        last_dur = self.rest_slope
        while t <= self.end_time:
            avl = self.whether_plane_avl(t)
            if avl:
                c_id = self.get_avl_plane(t)
                plane = self.plane_dict[c_id]
                last_dur = plane.left_dur
                plane.serve_and_update(t)
            else:
                if last_dur + self.rest_slope > self.full_dur:
                    last_dur = (last_dur + self.rest_slope) % self.full_dur
                else:
                    last_dur += self.rest_slope

                new_plane = Plane(id=id, t0=t, full_dur=self.full_dur, left_dur=last_dur,
                              upload_dur=self.upload_dur, leave_dur=self.leave_dur,
                              serve_dur=self.serve_dur,
                              return_dur=self.return_dur, unpack_dur=self.unpack_dur,
                              rest_dur=self.rest_dur)  # 初始化一辆新车

                new_plane.serve_and_update(t)
                self.plane_dict[new_plane.id] = new_plane
                id += 1

            t += self.max_gap

    def generate_min_plane_num(self):
        self.dig_info()
        self.get_plane_schedule()
        return len(self.plane_dict)

    def generate_schedule_df(self):
        record_dict = {}
        for c_id, plane in self.plane_dict.items():
            record = {k: '' for k in range(self.start_time, self.end_time + 1)}
            for t, event in plane.schedule.items():
                if 'serve' in event.keys():
                    serve_dur = event[
                                    'serve'] - plane.upload_dur - plane.leave_dur - plane.return_dur - plane.unpack_dur
                    curr_t = t

                    for i in range(plane.upload_dur):
                        record[curr_t] = Sign.upload
                        curr_t += 1

                    for i in range(plane.leave_dur):
                        record[curr_t] = Sign.leave
                        curr_t += 1

                    for i in range(serve_dur):
                        record[curr_t] = Sign.serve
                        curr_t += 1

                    for i in range(plane.return_dur):
                        record[curr_t] = Sign.back
                        curr_t += 1
                    for i in range(plane.unpack_dur):
                        record[curr_t] = Sign.unpack
                        curr_t += 1


                elif 'rest' in event.keys():
                    curr_t = t
                    for i in range(plane.rest_dur):
                        record[curr_t] = Sign.fix
                        curr_t += 1

            record_dict[c_id] = record

        out_df = pd.DataFrame(record_dict, dtype=object)
        out_df.replace('', Sign.spare, inplace=True)
        out_df = out_df.loc[self.start_time:self.end_time]
        out_df.set_axis(list(range(1, out_df.shape[1] + 1)), axis=1, inplace=True)
        self.schedule_df = out_df

        self.serve_distribution = dict()
        for hour, plane_status in self.schedule_df.iterrows():
            status_lt = list(plane_status)
            serve_num = status_lt.count(Sign.serve)
            self.serve_distribution[hour] = serve_num

    def output_schedule_df(self):
        self.schedule_df.to_csv('output.csv')

    def check_validity(self):
        lst = list(self.serve_distribution.values())
        try:
            first_satisfied = lst.index(self.serve_num)  # 找到第一个满足的位置
            return len(lst) - first_satisfied == lst.count(self.serve_num)
        except ValueError:
            return False

class planeType:
    def __init__(self, type, total_num,
                 upload_dur, leave_dur, serve_dur, return_dur, unpack_dur, rest_dur, full_dur):

        self.type = type
        self.total_num = total_num

        self.upload_dur = upload_dur
        self.leave_dur = leave_dur
        self.serve_dur = serve_dur
        self.return_dur = return_dur
        self.unpack_dur = unpack_dur
        self.rest_dur = rest_dur
        self.full_dur = full_dur

        self.capable_goods = set()
        self.max_serves = None

    def __repr__(self):
        return "planeType(type={}, total={}, max_serves={})".format(self.type, self.total_num, self.max_serves)

    def generate_max_serve_num(self, stTime, edTime):

        oneServe = singlePlaneEnv(start_time=stTime, end_time=edTime, serve_num=1,
                 upload_dur=self.upload_dur, unpack_dur=self.unpack_dur, leave_dur=self.leave_dur,
                 return_dur=self.return_dur, serve_dur=self.serve_dur, rest_dur=self.rest_dur,
                    full_dur=self.full_dur)
        plane4one = oneServe.generate_min_plane_num()
        min_serves = ceil(self.total_num / plane4one)

        curr_needed_planes = 0
        serve_num = min_serves
        while curr_needed_planes <= self.total_num:
            k = serve_num + 1
            currServe = singlePlaneEnv(start_time=stTime, end_time=edTime, serve_num=k,
                 upload_dur=self.upload_dur, unpack_dur=self.unpack_dur, leave_dur=self.leave_dur,
                 return_dur=self.return_dur, serve_dur=self.serve_dur, rest_dur=self.rest_dur,
                    full_dur=self.full_dur)
            curr_needed_planes = currServe.generate_min_plane_num()
            if curr_needed_planes <= self.total_num:
                serve_num += 1

        self.max_serves = serve_num
        logging.info("Max serving num for plane type {} is {}".format(self.type, self.max_serves))


class goodsType:
    def __init__(self, type, frozen_dur):

        self.type = type
        self.frozen_dur = frozen_dur

        self.capable_planes = set()

    def __repr__(self):
        return "goodsType(type={}, frozen_dur={})".format(self.type, self.frozen_dur)