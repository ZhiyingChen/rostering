from data_structure import Car
from config import planHorizon, Sign, CarSetting, read_config
import pandas as pd
from time import time

def judge_car_avl(t, car_dict):
    for c_id, car in car_dict.items():
        if car.is_able_work(t):
            return True
    return False

def get_avl_car(t, car_dict):
    best_c = None
    longest_spare_time = 0
    for c_id, car in car_dict.items():
        if car.is_able_work(t):
            if t - car.earliest_avl_time >= longest_spare_time:
                best_c = c_id
                longest_spare_time = t - car.earliest_avl_time
    return best_c


def run_greedy_algorithm():
    t = planHorizon.start_time  # plan horizon start time
    car_dict = {}

    id = 1
    while t <= planHorizon.end_time:
        if t == planHorizon.start_time:
            new_car = Car(id, t)
            id += 1

            serve_dur = new_car.get_serve_dur()
            new_car.update_left_work_dur_and_earliest_avl_time(serve_dur, t)

            car_dict[new_car.id] = new_car

            t += serve_dur
        else:
            car_avl = judge_car_avl(t, car_dict)
            if car_avl:
                c_id = get_avl_car(t, car_dict)
                car = car_dict[c_id]

                serve_dur = car.get_serve_dur()
                car.update_left_work_dur_and_earliest_avl_time(serve_dur, t)

                t += serve_dur
            else:
                new_car = Car(id, t)
                id += 1

                serve_dur = new_car.get_serve_dur()
                new_car.update_left_work_dur_and_earliest_avl_time(serve_dur, t)

                car_dict[new_car.id] = new_car

                t += serve_dur

    return car_dict


def greedy_output(car_dict):
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
    out_df.to_csv('greedy_output.csv')

if __name__ == '__main__':
    read_config()

    st = time()
    car_dict = run_greedy_algorithm()
    print(time() - st)
    greedy_output(car_dict)








