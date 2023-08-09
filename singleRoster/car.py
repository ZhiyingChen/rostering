from . import config as cg

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
        self.schedule[curr_t] = {cg.actionName.serve: (self.upload_dur + self.leave_dur + self.serve_dur + self.return_dur + self.unpack_dur + self.prepare_dur)}
        self.left_dur = self.left_dur - (self.upload_dur + self.leave_dur + self.serve_dur + self.return_dur + self.unpack_dur + self.prepare_dur)
        self.earliest_avl_time = curr_t + (self.upload_dur + self.leave_dur + self.serve_dur + self.return_dur + self.unpack_dur + self.prepare_dur)

        if not self.is_able_serve(self.earliest_avl_time):
            self.rest_and_update(self.earliest_avl_time)

    def rest_and_update(self, curr_t):
        self.schedule[curr_t] = {cg.actionName.rest: self.rest_dur}
        self.earliest_avl_time = curr_t + self.rest_dur
        self.left_dur = self.full_dur

    def __repr__(self):
        return "Car(id={}, avl={}, left={})".format(self.id, self.earliest_avl_time, self.left_dur)