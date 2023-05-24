from config import CarSetting
class Car:
    def __init__(self, id, t0, left_work_dur=CarSetting.init_left_work_dur):
        self.id = id
        self.earliest_avl_time = t0
        self.left_work_dur = left_work_dur

        self.upload_dur = CarSetting.upload_dur
        self.unpack_dur = CarSetting.unpack_dur
        self.leave_dur = CarSetting.leave_dur
        self.return_dur = CarSetting.return_dur
        self.min_serve_dur = CarSetting.min_serve_dur
        self.max_serve_dur = CarSetting.max_serve_dur
        self.rest_dur = CarSetting.rest_dur

        self.schedule = {}

    def is_able_work(self, curr_t):
        if self.earliest_avl_time <= curr_t and self.left_work_dur - self.leave_dur - self.return_dur >= self.min_serve_dur:
            return True
        return False

    def get_serve_dur(self):
        return min(self.max_serve_dur, self.left_work_dur - self.leave_dur - self.return_dur)


    def update_left_work_dur_and_earliest_avl_time(self, serve_dur, curr_t):
        # update left_work_dur
        self.left_work_dur = self.left_work_dur - serve_dur - self.leave_dur - self.return_dur

        # update earliest_avl_time
        if self.left_work_dur - self.leave_dur - self.return_dur < self.min_serve_dur:
            self.earliest_avl_time = curr_t + self.rest_dur + self.upload_dur + self.unpack_dur + self.leave_dur + self.return_dur + serve_dur
            self.schedule[curr_t] = {'serve': self.upload_dur + self.unpack_dur + self.leave_dur + self.return_dur + serve_dur}
            self.schedule[curr_t + self.upload_dur + self.unpack_dur + self.leave_dur + self.return_dur + serve_dur] = {'rest': self.rest_dur}
            self.left_work_dur = CarSetting.init_left_work_dur
        else:
            self.earliest_avl_time = curr_t + self.upload_dur + self.unpack_dur + self.leave_dur + self.return_dur + serve_dur
            self.schedule[curr_t] = {
                'serve': self.upload_dur + self.unpack_dur + self.leave_dur + self.return_dur + serve_dur}

    def update_rest_and_earliest_avl_time(self, curr_t):
        self.schedule[curr_t] = {'rest': self.rest_dur}
        self.earliest_avl_time = curr_t + self.rest_dur
        self.left_work_dur = CarSetting.init_left_work_dur