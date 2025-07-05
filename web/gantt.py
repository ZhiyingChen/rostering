from singleRoster.config import Sign

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

activity_map = {
    Sign.upload: "装货时间",
    Sign.unpack: "卸货时间",
    Sign.prepare: "备货时间",
    Sign.leave: "去程时间",
    Sign.back: "返程时间",
    Sign.serve: "服务时间",
    Sign.fix: "维修时间",
    Sign.spare: "空闲时间",
}

# 中文名 → 颜色
activity_color_map = {
    "装货时间": "#41337A",
    "卸货时间": "#4F3C7A",
    "备货时间": "#5D457A",
    "去程时间": "#8A2932",
    "返程时间": "#8A2933",
    "服务时间": "#78FF04",
    "维修时间": "#A29BFE",
    "空闲时间": "#E5E5E5",
}

def plot_gantt_bar(timeline_df: pd.DataFrame):
    fig = go.Figure()
    used_legend = set()

    for car in timeline_df.columns:
        y_label = f"Car{car}"
        series = timeline_df[car]
        prev_activity = None
        start = None

        for hour, activity in series.items():
            if activity == "SPARE":
                continue
            if activity != prev_activity:
                if prev_activity is not None:
                    label = activity_map[prev_activity]
                    show_legend = label not in used_legend
                    fig.add_trace(go.Bar(
                        x=[hour - start],
                        y=[y_label],
                        base=[start],
                        orientation='h',
                        name=label,
                        marker=dict(color=activity_color_map[label]),
                        hovertemplate=f"{label}<br>开始时间：{start}h<br>持续：{hour - start} 小时",
                        showlegend=show_legend
                    ))
                    used_legend.add(label)
                start = hour
                prev_activity = activity
        # 收尾
        if prev_activity is not None:
            label = activity_map[prev_activity]
            show_legend = label not in used_legend
            fig.add_trace(go.Bar(
                x=[hour + 1 - start],
                y=[y_label],
                base=[start],
                orientation='h',
                name=label,
                marker=dict(color=activity_color_map[label]),
                hovertemplate=f"{label}<br>开始时间：{start}h<br>持续：{hour + 1 - start} 小时",
                showlegend=show_legend
            ))
            used_legend.add(label)

    fig.update_layout(
        barmode='stack',
        title="📊 排产结果展示（小时刻度甘特图）",
        xaxis=dict(title="时间（小时）", tickfont=dict(size=12)),
        yaxis=dict(title="车辆", tickfont=dict(size=12), automargin=True),
        legend_title_text="活动类型",
        height=400 + len(timeline_df.columns) * 40,
        plot_bgcolor='white',
        margin=dict(l=100, r=30, t=60, b=40),
        font=dict(family="Microsoft YaHei, sans-serif", size=13)
    )
    st.plotly_chart(fig, use_container_width=True)

