import streamlit as st
from web import function

if __name__ == '__main__':
    st.set_page_config(
        page_title="车辆轮转算法平台",
        page_icon="📦",
        layout="wide"
    )
    # 渲染语言栏
    function.render_language_selector()
    lang, T = function.get_language_dict("app")


    st.title(T["page_title"])
    st.markdown(T["welcome_message"])
    st.markdown(T["navigation_guide"])

    function.render_footer()


