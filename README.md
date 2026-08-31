# 数据看板模板库 Dashboard Templates

**在线演示：https://dashboard-fj2hbfgjqfd2g5dwcnxkk5.streamlit.app/**

交互式数据看板模板集：上传数据、筛选下钻、一键导出。技术栈 Streamlit + pandas + Plotly。

## 模板

1. Excel 一键变看板 — 上传 Excel/CSV 自动生成图表
2. 财务经营分析 — 损益、现金流、预算 vs 实际、同环比
3. 电商运营 — 销售趋势、转化漏斗、复购、SKU 排行
4. 基金定投/组合回测
5. HR/问卷数据分析

所有演示数据均为程序生成的假数据。

## 本地运行

```
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/streamlit run app.py
```
