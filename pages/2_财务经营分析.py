from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from components.export import excel_download_button, pdf_download_button
from components.layout import page_header, setup_page
from components.metrics import metric_row
from lib.finance_calc import EXPENSE_COLS, enrich, fmt_pct, fmt_pp, fmt_wan, window_kpis
from theme import tokens

setup_page("财务经营分析", "💰")
page_header(
    "💰 财务经营分析",
    "把月度损益和现金流变成一眼能读懂的经营视图：营收是否兑现预算、钱花在哪、"
    "现金流是否健康。换上你的月度数据即可复用。（当前为程序生成的演示数据）",
)

_CSV = Path(__file__).resolve().parent.parent / "data" / "samples" / "finance_monthly.csv"


@st.cache_data
def load() -> pd.DataFrame:
    df = pd.read_csv(_CSV)
    # 规范月份为零填充 YYYY-MM 并按月排序，兼容客户数据的 2026-1 之类写法
    df["月份"] = pd.PeriodIndex(df["月份"], freq="M").astype(str)
    return enrich(df.sort_values("月份").reset_index(drop=True))


df = load()
months = df["月份"].tolist()

_default_start = months[-12] if len(months) >= 12 else months[0]
start, end = st.select_slider(
    "月份范围", options=months, value=(_default_start, months[-1]), key="fin_range",
)
kpi = window_kpis(df, start, end)
cur, prev = kpi["cur"], kpi["prev"]
win = df[(df["月份"] >= start) & (df["月份"] <= end)]


def _delta_pct(key: str):
    if prev is None or prev[key] == 0:
        return None, None
    d = cur[key] / prev[key] - 1
    return f"{fmt_pct(d, signed=True)} vs 前{kpi['n']}个月", d >= 0


def _delta_pp(key: str):
    if prev is None:
        return None, None
    d = cur[key] - prev[key]
    return f"{fmt_pp(d)} vs 前{kpi['n']}个月", d >= 0


rev_d, rev_g = _delta_pct("营收")
np_d, np_g = _delta_pct("净利润")
nm_d, nm_g = _delta_pp("净利率")
bg_d, bg_g = _delta_pp("预算达成率")
metric_row([
    {"label": f"营收（{kpi['n']}个月累计）", "value": fmt_wan(cur["营收"]),
     "delta": rev_d, "good": rev_g},
    {"label": "净利润", "value": fmt_wan(cur["净利润"]), "delta": np_d, "good": np_g},
    {"label": "净利率", "value": fmt_pct(cur["净利率"]), "delta": nm_d, "good": nm_g},
    {"label": "预算达成率", "value": fmt_pct(cur["预算达成率"]), "delta": bg_d, "good": bg_g},
])

WAN = 10000


def _month_axis(fig: go.Figure) -> go.Figure:
    fig.update_xaxes(tickformat="%Y-%m")  # 避免英文月份格式
    return fig


c1, c2 = st.columns(2)
with c1:
    fig = go.Figure()
    fig.add_bar(x=win["月份"], y=win["营收"] / WAN, name="营收")
    fig.add_scatter(x=win["月份"], y=win["预算营收"] / WAN, name="预算营收",
                    mode="lines+markers")
    fig.update_layout(title="营收 vs 预算（万元）")
    st.plotly_chart(_month_axis(fig), width="stretch")
with c2:
    fig = go.Figure()
    fig.add_bar(x=win["月份"], y=win["净利润"] / WAN, name="净利润",
                marker_color=tokens.SERIES[2])
    fig.update_layout(title="净利润（万元）", showlegend=False)
    st.plotly_chart(_month_axis(fig), width="stretch")

c3, c4 = st.columns(2)
with c3:
    mode = st.radio("成本费用口径", ["金额（万元）", "占营收比"],
                    horizontal=True, key="fin_cost_mode", label_visibility="collapsed")
    fig = go.Figure()
    for col in ["营业成本", *EXPENSE_COLS]:
        y = win[col] / WAN if mode == "金额（万元）" else win[col] / win["营收"]
        fig.add_bar(x=win["月份"], y=y, name=col)
    fig.update_layout(title=f"成本费用结构（{mode}）", barmode="stack")
    if mode == "占营收比":
        fig.update_yaxes(tickformat=".0%")
    st.plotly_chart(_month_axis(fig), width="stretch")
with c4:
    fig = go.Figure()
    fig.add_bar(x=win["月份"], y=win["经营现金流入"] / WAN, name="经营流入")
    fig.add_bar(x=win["月份"], y=win["经营现金流出"] / WAN, name="经营流出",
                marker_color=tokens.SERIES[3])
    fig.add_scatter(x=win["月份"], y=win["净现金流"] / WAN, name="净现金流",
                    mode="lines+markers", line=dict(color=tokens.SERIES[5]))
    fig.update_layout(title="经营现金流（万元）", barmode="group")
    st.plotly_chart(_month_axis(fig), width="stretch")

with st.expander("月度明细与同环比", expanded=False):
    detail = pd.DataFrame({
        "月份": win["月份"],
        "营收(万)": (win["营收"] / WAN).round(1),
        "营收环比": win["营收环比"].map(lambda x: fmt_pct(x, signed=True) if pd.notna(x) else "—"),
        "营收同比": win["营收同比"].map(lambda x: fmt_pct(x, signed=True) if pd.notna(x) else "—"),
        "净利润(万)": (win["净利润"] / WAN).round(1),
        "净利润环比": win["净利润环比"].map(lambda x: fmt_pct(x, signed=True) if pd.notna(x) else "—"),
        "净利率": win["净利率"].map(fmt_pct),
        "预算达成率": win["预算达成率"].map(fmt_pct),
    })
    st.dataframe(detail, width="stretch", hide_index=True)

e1, e2, _ = st.columns([1, 1, 4])
with e1:
    excel_download_button({"月度明细": win.drop(columns=["营收环比", "营收同比",
                                                        "净利润环比", "净利润同比"]),
                           "同环比": detail}, "财务经营分析.xlsx")
with e2:
    pdf_download_button(
        f"财务经营摘要（{start} ~ {end}）",
        [("营收累计", fmt_wan(cur["营收"])), ("净利润", fmt_wan(cur["净利润"])),
         ("净利率", fmt_pct(cur["净利率"])), ("预算达成率", fmt_pct(cur["预算达成率"]))],
        ["数据为程序生成的演示数据；比率为区间加权口径。"],
        "财务经营摘要.pdf",
    )
st.caption("演示数据由程序生成；净利润 = 营收 − 营业成本 − 销售/管理/研发费用 + 其他收益。")
