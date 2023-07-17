import utils as ul
import data_structure as ds
import pandas as pd
from log_setup import setup_log
import logging

class Input:
    def __init__(self, input_folder, output_folder):
        setup_log(output_folder, section_name=input_folder)
        self.input_folder = input_folder
        self.planes = dict()
        self.goods = dict()
        self.plane_good_relation = dict()
        self.start_time = None
        self.end_time = None
        self.serve_num = None
        logging.info('start reading data from {}'.format(self.input_folder))

    def load_params(self):
        from utils import paramHeader as ph
        from utils import params as p

        param_df = pd.read_csv(self.input_folder + ul.PLAN_FILE,  dtype={ph.paramName: str, ph.paramVal: int})
        param_dict = dict(zip(param_df[ph.paramName], param_df[ph.paramVal]))
        self.start_time = param_dict[p.stTime]
        self.end_time = param_dict[p.edTime]
        self.serve_num = param_dict[p.serveNum]
        logging.info("Finish loading params.")


    def load_plane_info(self):
        from utils import planeInfoHeader as pih

        plane_df = pd.read_csv(self.input_folder + ul.PLANE_INFO_FILE, dtype={
            pih.planeType: str,
            pih.planeNum: int,
            pih.packDur: int,
            pih.unpackDur: int,
            pih.goDur: int,
            pih.returnDur: int,
            pih.serveDur: int,
            pih.restDur: int,
            pih.maxWorkDur: int
        })

        planes = dict()
        for idx, row in plane_df.iterrows():
            plane_type = ds.planeType(
                type=row[pih.planeType],
                max_num=row[pih.planeNum],
                upload_dur=row[pih.packDur],
                leave_dur=row[pih.goDur],
                serve_dur=row[pih.serveDur],
                return_dur=row[pih.returnDur],
                unpack_dur=row[pih.unpackDur],
                rest_dur=row[pih.restDur],
                full_dur=row[pih.maxWorkDur]
            )
            planes[plane_type.type] = plane_type

        logging.info("Finish loading plane type info.")
        return planes


    def load_data(self):
        self.load_params()
        self.planes = self.load_plane_info()

