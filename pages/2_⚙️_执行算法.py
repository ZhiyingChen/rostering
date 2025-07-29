import streamlit as st
import pandas as pd
import time
from web import function, gantt
from singleRoster import config as cg
from singleRoster.solver import Solver

# 渲染语言栏
function.render_language_selector()
lang, T = function.get_language_dict("algo")


st.title(T["page_title"])
st.markdown(T["description"])

# 输入接口文档
st.header(T["input_interface_header"])

with st.expander(T["global_params_expander"]):
    df_global_params = pd.DataFrame(T["global_params_table"], columns=T["global_params_field"])
    st.table(df_global_params)

    st.markdown(T["global_params_description"])

st.header(T["output_interface_header"])
with st.expander(T["vehicle_result_expander"]):
    st.markdown(T["vehicle_result_details"])

st.markdown("---")
# 示例数据展示
st.header(T["example_data_header"])

@st.cache_data
def load_csv(file):
    return pd.read_csv(file)

# 加载示例数据
global_df = load_csv("data/data.csv")

# 可编辑的 DataFrame
with st.expander(T["edit_global_params"]):
    edited_global_df = st.data_editor(global_df, num_rows="dynamic")
    # 下载按钮
    st.download_button(
        label=T["download_global_params"],
        data=edited_global_df.to_csv(index=False).encode('utf-8'),
        file_name="全局参数.csv",
        mime="text/csv"
    )

# 显示运行按钮
if st.button(T["run_algorithm"]):
    with st.spinner(T["running_algorithm"]):
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
                         config_df=edited_global_df
                         )

            env.read_config()
            env.generate_car_schedule()
            env.generate_car_distribution()
            print("The validity of this schedule is {}".format(env.check_validity4dist()))

            result_df = env.output_df()
            st.success(T["algorithm_success"].format(round(time.time() - st_time)))
        except Exception as e:
            st.error(T["algorithm_error"].format(e))

        st.markdown("---")
        st.header(T["output_results"].format(len(result_df.columns)))

        with st.expander(T["vehicle_execution_results"]):
            st.dataframe(result_df)
            st.download_button(
                label=T["download_vehicle_results"],
                data=result_df.to_csv(index=False),
                file_name="车辆和执行结果.csv",
                mime="text/csv"
            )
        with st.spinner(T["drawing_gantt_chart"]):
            gantt.plot_gantt_bar(result_df)

function.render_footer()
