from config import CarSetting, planHorizon, Sign, read_config
from data_structure import Car
from math import floor, ceil
import pandas as pd
from time import time

def get_valid_car_num(greedy_car_dict):
    num = 0
    for c_id, car in greedy_car_dict.items():
        valid_schedule = {k: v for k, v in car.schedule.items() if k <= planHorizon.start_time + CarSetting.rest_dur}
        if len(valid_schedule):
            num += 1
    return num

def judge_car_avl(t, car_dict):
    for c_id, car in car_dict.items():
        if car.is_able_work_v2(t):
            return True
    return False

def get_avl_car(t, car_dict):
    best_c = None
    min_left_dur = float('inf')
    for c_id, car in car_dict.items():
        if car.is_able_work_v2(t):
            if car.left_total_dur <= min_left_dur:
                best_c = c_id
                min_left_dur = car.left_total_dur
    return best_c


def output(car_dict):
    record_dict = {}
    for c_id, car in car_dict.items():
        record = {k: '' for k in range(planHorizon.start_time, planHorizon.end_time + 1)}
        for t, event in car.schedule.items():
            if 'serve' in event.keys():
                serve_dur = event['serve'] - car.upload_dur - car.leave_dur - car.return_dur - car.unpack_dur - car.prepare_dur
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
                if t == 0:
                    curr_t = t
                    for i in range(car.rest_dur):
                        record[curr_t] = Sign.fix
                        curr_t += 1
                else:
                    curr_t = t - car.prepare_dur
                    for i in range(-car.prepare_dur, car.rest_dur):
                        record[curr_t] = Sign.fix
                        curr_t += 1

        record_dict[c_id] = record

    out_df = pd.DataFrame(record_dict, dtype=object)
    out_df.replace('', Sign.spare, inplace=True)
    out_df = out_df.loc[planHorizon.start_time:planHorizon.end_time]
    out_df.to_csv('output.csv')

if __name__ == '__main__':

    read_config()

    st = time()
    one_round_dur = CarSetting.upload_dur + CarSetting.leave_dur + CarSetting.max_serve_dur + CarSetting.return_dur + CarSetting.unpack_dur + CarSetting.prepare_dur # 跑一趟需要的总时长
    one_round_work_dur = CarSetting.leave_dur + CarSetting.max_serve_dur + CarSetting.return_dur   # 跑一趟需要的工作时长
    continuous_round_num = floor(CarSetting.init_left_work_dur / one_round_work_dur)            # 保养之前可以连续跑几趟车


    interval = ceil(one_round_dur / CarSetting.max_serve_dur) * CarSetting.max_serve_dur  # 同一辆车的最小发车间隔
    rest_round_num = ceil(CarSetting.rest_dur / interval)


    rest_slope = rest_round_num * one_round_dur   # 每两辆车之间需要错开的剩余总时间
    init_total_dur = one_round_dur * continuous_round_num

    last_left_work_dur = 0
    t = planHorizon.start_time



    car_dict = {}

    id = 1
    new_car = Car(id, t, left_total_dur=last_left_work_dur)  # 初始化一辆新车
    new_car.init_left_total_dur = init_total_dur
    if last_left_work_dur == 0:
        new_car.update_rest_and_earliest_avl_time_v2(t)

    car_dict[new_car.id] = new_car
    id += 1


    while t <= planHorizon.end_time:
        avl = judge_car_avl(t, car_dict)
        if avl:
            c_id = get_avl_car(t, car_dict)
            car = car_dict[c_id]

            car.update_left_total_dur_and_earliest_avl_time(t)
            t += CarSetting.max_serve_dur
        else:
            car = car_dict[id - 1]
            last_action_key = max(car.schedule.keys())
            last_action = car.schedule[last_action_key]
            if 'serve' in last_action:
                last_left_total_dur = car.left_total_dur + last_action['serve']
            else:
                last_left_total_dur = 0

            if last_left_total_dur + rest_slope > init_total_dur:
                left_total_dur = (last_left_total_dur + rest_slope) % init_total_dur
            else:
                left_total_dur = last_left_total_dur + rest_slope
            new_car = Car(id, t, left_total_dur=left_total_dur)  # 初始化一辆新车
            new_car.init_left_total_dur = init_total_dur
            new_car.update_left_total_dur_and_earliest_avl_time(t)
            car_dict[new_car.id] = new_car
            id += 1

            t += CarSetting.max_serve_dur

    print(time() - st)
    output(car_dict)


