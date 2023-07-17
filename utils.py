PLANE_INFO_FILE = '/飞机信息.csv'
GOODS_INFO_FILE = '/货物信息.csv'
PLAN_FILE = '/参数表.csv'
PLANE_GOODS_RELATION_FILE = '/飞机货物匹配关系.csv'

class planeInfoHeader:
    planeType = '飞机类型'
    planeNum = '飞机数量'
    packDur = '装货时间'
    unpackDur = '卸货时间'
    goDur = '去程时间'
    returnDur = '返程时间'
    serveDur = '服务时间'
    restDur = '维修时间'
    maxWorkDur = '最大工作时间'

class goodsInfoHeader:
    goodsType = '货物类型'
    frozenDur = '冷冻时长'

class paramHeader:
    paramName = '参数名称'
    paramVal = '参数值'


class params:
    stTime = '计划开始时刻'
    edTime = '计划结束时刻'
    serveNum = '同时服务数量'

class planeGoodsRelatHeader:
    planeType = '飞机类型'
    goodsType = '货物类型'