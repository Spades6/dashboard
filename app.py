import streamlit as st

st.set_page_config(page_title="数据看板模板库", page_icon="📊", layout="wide")

st.title("📊 数据看板模板库")
st.caption("交互式数据看板模板：上传数据、筛选下钻、一键导出。所有演示数据均为程序生成的假数据。")

st.page_link("pages/1_Excel一键看板.py", label="Excel 一键变看板 — 上传即出图", icon="⚡")
st.page_link("pages/2_财务经营分析.py", label="财务经营分析 — 损益 / 现金流 / 预算达成", icon="💰")
st.page_link("pages/3_电商运营.py", label="电商运营 — 趋势 / 漏斗 / 复购 / SKU", icon="🛒")
st.page_link("pages/4_基金回测.py", label="基金定投 / 组合回测", icon="📈")
st.page_link("pages/5_HR问卷分析.py", label="HR / 问卷数据分析", icon="🧑‍💼")
