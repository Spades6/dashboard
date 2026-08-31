from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from components.export import excel_download_button, pdf_download_button
from components.filters import date_range_filter, multiselect_filter
from components.layout import page_header, setup_page
from components.metrics import metric_row
from lib.fund_calc import (annualized_return, annualized_vol, dca_simulate,
                           drawdown_series, max_drawdown, period_return, rebase)
from theme import tokens

setup_page("基金回测", "📈")
page_header(
    "📈 基金定投 / 组合回测",
    "净值对比、定投模拟、回撤分析一页看全——把「长期定投到底值不值」算给你看。",
)
st.info("本页为看板模板演示：基金与净值均为**程序生成的虚构数据**，不对应任何真实产品，"
        "亦不构成任何投资建议。", icon="⚠️")

_CSV = Path(__file__).resolve().parent.parent / "data" / "samples" / "fund_nav.csv"


@st.cache_data
def load() -> pd.DataFrame:
    return pd.read_csv(_CSV, parse_dates=["日期"]).sort_values(["基金名称", "日期"])


nav_all = load()
funds = sorted(nav_all["基金名称"].unique())
dmin, dmax = nav_all["日期"].min().date(), nav_all["日期"].max().date()

f1, f2 = st.columns([2, 2])
with f1:
    picked = multiselect_filter("对比基金", funds, "fd_funds")
with f2:
    start, end = date_range_filter("回测区间", dmin, dmax, "fd_range")

f3, f4 = st.columns([2, 2])
with f3:
    dca_fund = st.selectbox("定投标的", picked, key="fd_dca")
with f4:
    amount = st.number_input("每月定投金额（元）", min_value=100, max_value=100000,
                             value=1000, step=100, key="fd_amt")

sel = nav_all[(nav_all["日期"].dt.date >= start) & (nav_all["日期"].dt.date <= end)
              & nav_all["基金名称"].isin(picked)]
if sel.empty or dca_fund is None:
    st.warning("所选区间没有净值数据——放宽区间或基金试试。")
    st.stop()

dca_df = sel[sel["基金名称"] == dca_fund][["日期", "单位净值"]].reset_index(drop=True)
dca = dca_simulate(dca_df, amount)
lump = period_return(dca_df["单位净值"])
metric_row([
    {"label": f"定投·累计投入（{dca['months']} 期）", "value": f"¥{dca['invested']:,.0f}"},
    {"label": "定投·期末市值", "value": f"¥{dca['value']:,.0f}"},
    {"label": "定投收益率", "value": f"{dca['return_rate']:+.1%}",
     "delta": f"同期一次性买入 {lump:+.1%}", "good": dca['return_rate'] >= lump},
    {"label": f"{dca_fund}·最大回撤", "value": f"{max_drawdown(dca_df['单位净值']):.1%}"},
])

g1, g2 = st.columns(2)
with g1:
    fig = go.Figure()
    for name, grp in sel.groupby("基金名称"):
        fig.add_scatter(x=grp["日期"], y=rebase(grp["单位净值"].reset_index(drop=True)) - 1,
                        name=name, mode="lines")
    fig.update_layout(title="累计收益对比（区间起点归一）")
    fig.update_yaxes(tickformat="+.0%")
    st.plotly_chart(fig, width="stretch")
with g2:
    dd = drawdown_series(dca_df["单位净值"])
    fig = go.Figure(go.Scatter(x=dca_df["日期"], y=dd, mode="lines",
                               line=dict(color=tokens.SERIES[7]),
                               fill="tozeroy", fillcolor="rgba(227,73,72,0.10)"))
    fig.update_layout(title=f"{dca_fund}·回撤走势", showlegend=False)
    fig.update_yaxes(tickformat=".0%")
    st.plotly_chart(fig, width="stretch")

rows = []
for name, grp in sel.groupby("基金名称"):
    nav = grp["单位净值"].reset_index(drop=True)
    rows.append({"基金": name,
                 "区间收益": f"{period_return(nav):+.1%}",
                 "年化收益": f"{annualized_return(nav):+.1%}",
                 "年化波动": f"{annualized_vol(nav):.1%}",
                 "最大回撤": f"{max_drawdown(nav):.1%}"})
metrics_df = pd.DataFrame(rows)
st.dataframe(metrics_df, width="stretch", hide_index=True)

e1, e2, _ = st.columns([1, 1, 4])
with e1:
    excel_download_button({"指标": metrics_df, "净值": sel}, "基金回测.xlsx")
with e2:
    pdf_download_button(
        f"基金回测摘要（{start} ~ {end}）",
        [("定投标的", dca_fund), ("累计投入", f"¥{dca['invested']:,.0f}"),
         ("期末市值", f"¥{dca['value']:,.0f}"), ("定投收益率", f"{dca['return_rate']:+.1%}"),
         ("同期一次性买入", f"{lump:+.1%}")],
        ["基金与净值均为程序生成的虚构数据，不构成投资建议。",
         "定投口径：每月首个交易日按当日净值买入固定金额。"],
        "基金回测摘要.pdf",
    )
st.caption("定投口径：每月首个交易日买入；年化按 250 交易日；虚构演示数据，非投资建议。")
