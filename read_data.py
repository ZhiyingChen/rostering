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
        self.plane_goods_relation = set()
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
                total_num=row[pih.planeNum],
                upload_dur=row[pih.packDur],
                leave_dur=row[pih.goDur],
                serve_dur=row[pih.serveDur],
                return_dur=row[pih.returnDur],
                unpack_dur=row[pih.unpackDur],
                rest_dur=row[pih.restDur],
                full_dur=row[pih.maxWorkDur]
            )
            planes[plane_type.type] = plane_type

        logging.info("Finish loading plane type info: {}".format(len(planes)))
        return planes

    def load_goods_info(self):
        from utils import goodsInfoHeader as gih

        goods_df = pd.read_csv(self.input_folder + ul.GOODS_INFO_FILE,
                               dtype={gih.goodsType: str, gih.frozenDur: int})

        goods = dict()
        for idx, row in goods_df.iterrows():
            goods_type = ds.goodsType(
                type=row[gih.goodsType],
                frozen_dur=row[gih.frozenDur]
            )
            goods[goods_type.type] = goods_type

        logging.info("Finish loading goods type info: {}".format(len(goods)))
        return goods

    def load_plane_goods_relation(self):
        from utils import planeGoodsRelatHeader as pgh

        plane_goods_relation_df = pd.read_csv(self.input_folder + ul.PLANE_GOODS_RELATION_FILE,
                                              dtype={pgh.planeType: str, pgh.goodsType: str})
        self.plane_goods_relation = set()
        for idx, row in plane_goods_relation_df.iterrows():
            if row[pgh.planeType] not in self.planes:
                logging.error("Plane type {} is not in plane list".format(row[pgh.planeType]))
                continue
                
            if row[pgh.goodsType] not in self.goods:
                logging.error("Goods type {} is not in goods list".format(row[pgh.goodsType]))
                continue

            self.plane_goods_relation.add((row[pgh.planeType], row[pgh.goodsType]))
            plane = self.planes[row[pgh.planeType]]
            plane.capable_goods.add(row[pgh.goodsType])
            
            goods = self.goods[row[pgh.goodsType]]
            goods.capable_planes.add(row[pgh.planeType])
            
        logging.info("Finish loading plane goods relation: {}".format(len(self.plane_goods_relation)))

    def load_data(self):
        self.load_params()
        self.planes = self.load_plane_info()
        self.goods = self.load_goods_info()
        self.load_plane_goods_relation()
        logging.info("Finish loading data.")

    def generate_max_serves4planes(self):
        for p, plane_type in self.planes.items():
            plane_type.generate_max_serve_num(stTime=self.start_time, edTime=self.end_time)

    def generate_data(self):
        self.load_data()
        self.generate_max_serves4planes()
