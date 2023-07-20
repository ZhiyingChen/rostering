from config import Sign
from config import paramHeader as ph

import time
import plotly as py
import plotly.figure_factory as ff
import pandas as pd
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)


def assign_color(df):
    activities = [
        Sign.upload,
        Sign.unpack,
        Sign.prepare,
        Sign.leave,
        Sign.back,
        Sign.serve,
        Sign.fix,
    ]

    nameMap = {
        Sign.upload: ph.packDur,
        Sign.unpack: ph.unpackDur,
        Sign.prepare: ph.prepareDur,
        Sign.leave: ph.goDur,
        Sign.back: ph.returnDur,
        Sign.serve: ph.serveDur,
        Sign.fix: ph.restDur,
    }

    # activityMap = dict()
    # for i, value in enumerate(activities):
    #     activityMap[nameMap[value]] = 'rgb({0})'.format(str(list(np.random.choice(range(256), size=3)))[1:-1])

    activityMap = {
        ph.packDur: 'rgb(64, 53, 120)',
        ph.unpackDur: 'rgb(65, 53, 120)',
        ph.prepareDur: 'rgb(66, 53, 120)',
        ph.goDur: 'rgb(138, 41, 50)',
        ph.returnDur: 'rgb(138, 41, 51)',
        ph.serveDur: 'rgb(120, 255, 4)',
        ph.restDur: 'rgb(126, 54, 221)',
    }

    return nameMap, activityMap

def create_draw_defination():
    df = []
    for index in range(len(n_job_id)):
        operation = {}
        # 机器，纵坐标
        operation['Task'] = n_bay_text.__getitem__(index)
        operation['Start'] = start_time.__add__(n_start_time.__getitem__(index) * millis_seconds_per_hour)
        operation['Finish'] = start_time.__add__(
            (n_start_time.__getitem__(index) + n_duration_time.__getitem__(index)) * millis_seconds_per_hour)
        # 工件，
        # job_num = op.index(n_job_id.__getitem__(index)) + 1
        operation['Resource'] = n_job_id.__getitem__(index)
        # operation['Complete'] = n_bay_start.__getitem__(index)+1
        df.append(operation)
    df.sort(key=lambda x: x["Task"], reverse=True)
    print(df)
    return df


def draw_prepare():
    df = create_draw_defination()
    return ff.create_gantt(df, colors=activityMap, index_col='Resource',
                           title='display', show_colorbar=True,
                           group_tasks=True, data=n_duration_time,
                           showgrid_x=True, showgrid_y=True)


def add_annotations(fig):
    y_pos = 0
    for index in range(len(n_job_id)):
        # 机器，纵坐标
        y_pos = n_bay_start.__getitem__(index)

        x_start = start_time.__add__(n_start_time.__getitem__(index) * millis_seconds_per_hour)
        x_end = start_time.__add__(
            (n_start_time.__getitem__(index) + n_duration_time.__getitem__(index)) * millis_seconds_per_hour)
        x_pos = (x_end - x_start) / 2 + x_start

        # 工件，
        # job_num = op.index(n_job_id.__getitem__(index)) + 1
        # text = 'J(' + str(job_num) + "," + str(get_op_num(job_num)) + ")=" + str(n_duration_time.__getitem__(index))
        # text = 'T' + str(job_num) + str(get_op_num(job_num))
        text = ""
        text_font = dict(size=14, color='black')
        fig['layout']['annotations'] += tuple(
            [dict(x=x_pos, y=y_pos, text=text, textangle=-30, showarrow=False, font=text_font)])


def draw_gantt():
    fig = draw_prepare()
    add_annotations(fig)
    py.offline.plot(fig, filename='gantt.html')

if __name__ == '__main__':

    out_df = pd.read_csv('output.csv', index_col=0, dtype=object)
    nameMap, activityMap = assign_color(out_df)
    cars = list(out_df.columns)
    millis_seconds_per_hour = 1000 * 60 * 60
    start_time = time.time() * 1000

    n_start_time = []
    n_end_time = []
    n_duration_time = []
    n_bay_start = []
    n_bay_text = []
    n_job_id = []
    colors = []

    for car in cars:
        car_timeline = out_df[car]
        dic = dict(car_timeline)

        for hour, activity in dic.items():
            if dic[hour] == Sign.spare:
                continue
            if activity == dic.get(hour-1, None):
                continue
            timeBegin = hour

            i = 0
            curr_t = hour
            while dic.get(curr_t, None) == activity:
                curr_t += 1
                i += 1

            timeEnd = curr_t
            duration = i
            n_start_time.append(timeBegin)
            n_end_time.append(timeEnd)
            n_duration_time.append(duration)
            n_bay_start.append(int(car)-1)
            n_bay_text.append('Car' + car)
            n_job_id.append(nameMap[activity])
            color = activityMap[nameMap[activity]]
            colors.append(color)

    draw_gantt()

