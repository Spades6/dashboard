import pandas as pd
import plotly.express as px
import streamlit as st

from components.export import excel_download_button, pdf_download_button
from components.layout import page_header, setup_page
from components.metrics import metric_row

setup_page("数据看板模板库", "📊")
page_header("📊 数据看板模板库",
            "交互式数据看板模板：上传数据、筛选下钻、一键导出。所有演示数据均为程序生成的假数据。")

st.page_link("pages/1_Excel一键看板.py", label="Excel 一键变看板 — 上传即出图", icon="⚡")
st.page_link("pages/2_财务经营分析.py", label="财务经营分析 — 损益 / 现金流 / 预算达成", icon="💰")
st.page_link("pages/3_电商运营.py", label="电商运营 — 趋势 / 漏斗 / 复购 / SKU", icon="🛒")
st.page_link("pages/4_基金回测.py", label="基金定投 / 组合回测", icon="📈")
st.page_link("pages/5_HR问卷分析.py", label="HR / 问卷数据分析", icon="🧑‍💼")

st.divider()
st.subheader("组件与主题预览")

metric_row([
    {"label": "本月营收", "value": "¥1,284 万", "delta": "+12.4% vs 上月", "good": True},
    {"label": "净利率", "value": "18.6%", "delta": "-0.8pp vs 上月", "good": False},
    {"label": "活跃客户", "value": "3,207", "delta": "+204 vs 上月", "good": True},
    {"label": "预算达成", "value": "96.2%"},
])

_demo = pd.DataFrame({
    "月份": ["1月", "2月", "3月", "4月", "5月", "6月"] * 2,
    "金额": [980, 1040, 1130, 1090, 1210, 1284, 820, 850, 940, 930, 990, 1045],
    "口径": ["营收"] * 6 + ["成本"] * 6,
})
fig = px.line(_demo, x="月份", y="金额", color="口径", title="营收与成本走势（演示数据，万元）")
st.plotly_chart(fig, width="stretch")

col1, col2, _ = st.columns([1, 1, 4])
with col1:
    excel_download_button({"演示数据": _demo}, "demo.xlsx")
with col2:
    pdf_download_button(
        "演示报告", [("本月营收", "¥1,284 万"), ("净利率", "18.6%")],
        ["以上为程序生成的演示数据，仅用于展示导出能力。"], "demo.pdf",
    )
