import streamlit as st
import pandas as pd
import time
from web import function
from singleRoster import config as cg
from singleRoster.solver import Solver

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
    ], columns=["字段名称", "类型", "描述"])
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

st.header("📥 输出接口文档")
with st.expander("📥 输出文件说明：车辆和执行结果.csv"):
    st.markdown(
        """
        每一行代表时间（小时），每一列代表每辆车，内容值含义如下
        - 装货： 0
        - 出发： 1
        - 服务： 2
        - 返回： 3
        - 卸货： 4
        - 备货： 5
        - 维修： 6
        - 空闲： 7
        """
    )

st.markdown("---")
# 示例数据展示
st.header("📄 示例输入数据（可编辑）")


@st.cache_data
def load_csv(file):
    return pd.read_csv(file)


# 加载示例数据
global_df = load_csv("data/data.csv")

# 可编辑的 DataFrame
with st.expander("📝 编辑全局参数"):
    edited_global_df = st.data_editor(global_df, num_rows="dynamic")
    # 下载按钮
    st.download_button(
        label="📥 下载编辑后的 全局参数.csv",
        data=edited_global_df.to_csv(index=False).encode('utf-8'),
        file_name="全局参数.csv",
        mime="text/csv"
    )

# 显示运行按钮
if st.button("🚀 运行算法"):
    with st.spinner("算法运行中，请稍候..."):
        try:
            st_time = time.time()

            env = Solver(stTime=cg.planHorizon.start_time, edTime=cg.planHorizon.end_time,
                         serveNum=cg.serveInfo.serveNum,
                         upload_dur=cg.CarSetting.upload_dur, unpack_dur=cg.CarSetting.unpack_dur,
                         prepare_dur=cg.CarSetting.prepare_dur,
                         leave_dur=cg.CarSetting.leave_dur, return_dur=cg.CarSetting.leave_dur,
                         serve_dur=cg.CarSetting.serve_dur,
                         rest_dur=cg.CarSetting.rest_dur, full_dur=cg.CarSetting.full_dur,
                         load_from_file=False,
                         config_df=global_df
                         )

            env.read_config()
            env.generate_car_schedule()
            env.generate_car_distribution()
            print("The validity of this schedule is {}".format(env.check_validity4dist()))

            result_df = env.output_df()
            st.success("✅ 算法运行完成！耗时{}秒".format(round(time.time() - st_time)))
        except Exception as e:
            st.error(f"❌ 算法运行出错：{e}")

        st.markdown("---")
        st.header("📊 输出结果")

        with st.expander("📄 车辆和执行结果"):
            st.dataframe(result_df)
            st.download_button(
                label=f"📥 下载 车辆和执行结果.csv",
                data=result_df.to_csv(index=False),
                file_name="车辆和执行结果.csv",
                mime="text/csv"
            )


function.render_footer()
