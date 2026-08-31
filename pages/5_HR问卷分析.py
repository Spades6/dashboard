from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from components.export import excel_download_button, pdf_download_button
from components.filters import multiselect_filter
from components.layout import page_header, setup_page
from components.metrics import metric_row
from lib.hr_calc import SURVEY_DIMS, attrition_by_dept, nps, satisfaction_matrix
from theme import tokens

setup_page("HR/问卷分析", "🧑‍💼")
page_header(
    "🧑‍💼 HR / 问卷数据分析",
    "人员结构、离职风险、满意度短板一页看清——把年度敬业度调研从 Excel 里解放出来。"
    "（当前为程序生成的演示数据）",
)

_DIR = Path(__file__).resolve().parent.parent / "data" / "samples"


@st.cache_data
def load():
    return pd.read_csv(_DIR / "hr_roster.csv"), pd.read_csv(_DIR / "hr_survey.csv")


roster_all, survey_all = load()
depts = multiselect_filter("部门", sorted(roster_all["部门"].unique()), "hr_dept")
roster = roster_all[roster_all["部门"].isin(depts)]
survey = survey_all[survey_all["部门"].isin(depts)]

if roster.empty or survey.empty:
    st.warning("筛选条件下没有人员或问卷数据——放宽部门筛选试试。")
    st.stop()

active = int((roster["在职状态"] == "在职").sum())
left = int((roster["在职状态"] == "本年离职").sum())
metric_row([
    {"label": "在职人数", "value": f"{active:,}"},
    {"label": "本年离职率", "value": f"{left / (active + left):.1%}"},
    {"label": "敬业度均值（1-5）", "value": f"{survey['敬业度'].mean():.2f}"},
    {"label": "NPS", "value": f"{nps(survey['NPS']) * 100:+.0f}"},
])

att = attrition_by_dept(roster)
g1, g2 = st.columns(2)
with g1:
    fig = go.Figure(go.Bar(x=att["部门"], y=att["在职人数"]))
    fig.update_layout(title="在职人数·按部门", showlegend=False)
    st.plotly_chart(fig, width="stretch")
with g2:
    fig = go.Figure(go.Bar(x=att["部门"], y=att["离职率"],
                           marker_color=tokens.SERIES[1]))
    fig.update_layout(title="本年离职率·按部门", showlegend=False)
    fig.update_yaxes(tickformat=".0%")
    st.plotly_chart(fig, width="stretch")

g3, g4 = st.columns(2)
with g3:
    dim = st.radio("分布维度", ["年龄", "司龄"], horizontal=True,
                   key="hr_dim", label_visibility="collapsed")
    fig = go.Figure(go.Histogram(x=roster[dim], nbinsx=20,
                                 marker_color=tokens.SERIES[2]))
    fig.update_layout(title=f"{dim}分布（人数）", showlegend=False, bargap=0.05)
    st.plotly_chart(fig, width="stretch")
with g4:
    m = satisfaction_matrix(survey)
    scale = [[i / (len(tokens.SEQ_BLUE[:8]) - 1), c]
             for i, c in enumerate(tokens.SEQ_BLUE[:8])]
    fig = go.Figure(go.Heatmap(
        z=m.values, x=list(m.columns), y=list(m.index),
        colorscale=scale, zmin=1, zmax=5,
        texttemplate="%{z:.2f}", textfont=dict(color=tokens.INK),
        colorbar=dict(title="均值"),
    ))
    fig.update_layout(title="满意度五维·按部门（1-5）")
    st.plotly_chart(fig, width="stretch")

nps_dist = survey["NPS"].value_counts().reindex(range(11), fill_value=0)
fig = go.Figure(go.Bar(x=nps_dist.index, y=nps_dist.values))
fig.update_layout(title="NPS 打分分布（0-10 分，9-10 为推荐者，0-6 为贬损者）",
                  showlegend=False)
fig.update_xaxes(dtick=1)
st.plotly_chart(fig, width="stretch")

e1, e2, _ = st.columns([1, 1, 4])
with e1:
    excel_download_button({"部门离职": att, "满意度矩阵": m.reset_index()}, "HR分析.xlsx")
with e2:
    pdf_download_button(
        "HR / 问卷分析摘要",
        [("在职人数", f"{active:,}"), ("本年离职率", f"{left / (active + left):.1%}"),
         ("敬业度均值", f"{survey['敬业度'].mean():.2f}"),
         ("NPS", f"{nps(survey['NPS']) * 100:+.0f}")],
        ["数据为程序生成的演示数据。", "NPS = 推荐者(9-10)占比 − 贬损者(0-6)占比。"],
        "HR分析摘要.pdf",
    )
st.caption("口径：离职率=本年离职/(在职+本年离职)；NPS=推荐者占比−贬损者占比（×100）。")
