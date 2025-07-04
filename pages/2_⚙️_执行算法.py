import streamlit as st
import pandas as pd
import time
from web import function

st.title("⚙️ 汽车轮转与维修调度算法")

st.markdown(
    """
    请在“执行算法”页面将示例输入文件改成你需要的数据。
    """
)

# 输入接口文档
# 输入接口文档
st.header("📥 输入接口文档")

with st.expander("📥 输入文件说明：全局参数.csv"):
    df_global_params = pd.DataFrame([
        ["参数名称", "str", "各类参数的名称"],
        ["参数值", "double", "参数值"]
    ], columns=["字段名称","类型", "描述"])
    st.table(df_global_params)

    st.markdown("""
        **参数枚举说明：**
        以下是各个参数的定义和含义：
    
        - **t_pack**：装货时间，车辆在装货点需要花费的时间。
        - **t_unpack**：卸货时间，车辆在卸货点需要花费的时间。
        - **t_pre**：备货时间，车辆在维修点进行备货的时间，这部分时间可以计入维修时间。
        - **t_go**：去程时间，车辆从起点出发到达服务区域的时间。
        - **t_back**：返程时间，车辆从服务区域返回起点的时间。
        - **t_serve**：单次服务时间（小时），车辆在服务区域内一次连续提供服务的时间。
        - **t_rest**：维修时间（小时），车辆进行维修所需的时间。
        - **t_work**：每辆车的最大累计工作时间（小时），车辆在进行服务和维修之前可以累计的最大工作时间。
        - **t0 / t1**：起始时间 / 结束时间，服务时间的开始和结束的具体时间点。
        - **t_gap**：错峰时间间隔（小时），在排班时需要考虑的时间间隔，以避免车辆在同一时间段集中出发或返回。
    """)
function.render_footer()