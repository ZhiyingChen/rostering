import streamlit as st
from web import function

# 渲染语言栏
function.render_language_selector()
lang, T = function.get_language_dict("doc")

st.title(T["page_title"])

# 项目背景介绍
st.header(T["project_background_header"])
st.markdown(T["project_background_text"])

st.subheader(T["problem_description_subheader"])
# 插入问题描述图片
st.image("image/Question.png", caption=T["problem_description_image_caption"], width=800)
st.markdown(T["problem_description_details"])

function.render_footer()


