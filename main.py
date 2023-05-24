from greedy import run_greedy_algorithm
from config import CarSetting, planHorizon
from data_structure import Car
from math import floor, ceil
import pandas as pd

def get_valid_car_num(greedy_car_dict):
    num = 0
    for c_id, car in greedy_car_dict.items():
        valid_schedule = {k: v for k, v in car.schedule.items() if k <= planHorizon.start_time + CarSetting.rest_dur}
        if len(valid_schedule):
            num += 1
    return num

def get_avl_car(t, car_dict):
    best_c = None
    min_left_dur = float('inf')
    for c_id, car in car_dict.items():
        if car.is_able_work(t):
            if car.left_work_dur <= min_left_dur:
                best_c = c_id
                min_left_dur = car.left_work_dur
    return best_c

def output(car_dict):
    record_dict = {}
    for c_id, car in car_dict.items():
        record = {k: '' for k in range(planHorizon.start_time, planHorizon.end_time + 1)}
        for t, event in car.schedule.items():
            if 'serve' in event.keys():
                serve_dur = event['serve'] - car.upload_dur - car.leave_dur - car.return_dur - car.unpack_dur
                curr_t = t

                for i in range(car.upload_dur):
                    record[curr_t] = '↑'
                    curr_t += 1
                for i in range(car.leave_dur):
                    record[curr_t] = '→'
                    curr_t += 1

                for i in range(serve_dur):
                    record[curr_t] = '口'
                    curr_t += 1

                for i in range(car.return_dur):
                    record[curr_t] = '←'
                    curr_t += 1
                for i in range(car.unpack_dur):
                    record[curr_t] = '↓'
                    curr_t += 1
            elif 'rest' in event.keys():
                curr_t = t
                for i in range(car.rest_dur):
                    record[curr_t] = 'zZ'
                    curr_t += 1

        record_dict[c_id] = record

    out_df = pd.DataFrame(record_dict, dtype=object)
    out_df = out_df.T
    out_df.to_csv('output.csv')

if __name__ == '__main__':
    greedy_car_dict = run_greedy_algorithm()

    one_round_dur = CarSetting.upload_dur + CarSetting.leave_dur + CarSetting.max_serve_dur + CarSetting.return_dur + CarSetting.unpack_dur  # 跑一趟需要的总时长
    one_round_work_dur = CarSetting.leave_dur + CarSetting.max_serve_dur + CarSetting.return_dur   # 跑一趟需要的工作时长
    continuous_round_num = floor(CarSetting.init_left_work_dur / one_round_work_dur)            # 保养之前可以连续跑几趟车

    valid_car_num = get_valid_car_num(greedy_car_dict)     # 休息时间内，至少需要多少辆车正常工作
    interval = ceil(one_round_dur / CarSetting.max_serve_dur) * CarSetting.max_serve_dur  # 同一辆车的最小发车间隔
    gradient = CarSetting.rest_dur / interval   # 休息的时间可以跑几趟车
    rest_slope = gradient * one_round_work_dur  # 每两辆车之间需要错开的剩余工作时间

    car_num = ceil(valid_car_num * ((one_round_dur * continuous_round_num + CarSetting.rest_dur)/ (one_round_dur * continuous_round_num)))  # 至少需要几辆车

    init_points = [planHorizon.start_time + i * CarSetting.max_serve_dur for i in range(car_num)]

    car_dict = {}
    id = 0
    last_left_work_dur = rest_slope
    t = planHorizon.start_time
    while t <= planHorizon.end_time:

        if t in init_points:
            new_car = Car(id, t, left_work_dur=last_left_work_dur)  # 初始化一辆新车
            id += 1

            new_car.update_left_work_dur_and_earliest_avl_time(CarSetting.max_serve_dur, t)

            car_dict[new_car.id] = new_car
            if (last_left_work_dur + rest_slope) % CarSetting.init_left_work_dur == 0:
                last_left_work_dur = CarSetting.init_left_work_dur
            else:
                last_left_work_dur = (last_left_work_dur + rest_slope) % CarSetting.init_left_work_dur

        else:
            c_id = get_avl_car(t, car_dict)
            car = car_dict[c_id]
            car.update_left_work_dur_and_earliest_avl_time(CarSetting.max_serve_dur, t)

        t += CarSetting.max_serve_dur

    output(car_dict)