from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from components.export import excel_download_button, pdf_download_button
from components.filters import date_range_filter, multiselect_filter
from components.layout import page_header, setup_page
from components.metrics import metric_row
from lib.auto_profile import top_n
from lib.ecom_calc import funnel_totals, kpis, purchase_freq_dist, trend
from theme import tokens

setup_page("电商运营", "🛒")
page_header(
    "🛒 电商运营",
    "销售、转化、复购一屏看全：GMV 从哪来、流量在哪一步流失、谁在重复购买。"
    "换上你的订单明细即可复用。（当前为程序生成的演示数据）",
)

_DIR = Path(__file__).resolve().parent.parent / "data" / "samples"


@st.cache_data
def load():
    orders = pd.read_csv(_DIR / "ecom_orders.csv", parse_dates=["日期"])
    funnel = pd.read_csv(_DIR / "ecom_funnel.csv", parse_dates=["日期"])
    return orders, funnel


orders_all, funnel_all = load()
dmin, dmax = orders_all["日期"].min().date(), orders_all["日期"].max().date()

f1, f2, f3 = st.columns([2, 2, 1])
with f1:
    start, end = date_range_filter("日期范围", dmin, dmax, "ec_range")
with f2:
    channels = multiselect_filter("渠道", sorted(orders_all["渠道"].unique()), "ec_ch")
with f3:
    freq_label = st.radio("趋势粒度", ["按日", "按周", "按月"], index=2,
                          horizontal=True, key="ec_freq")

mask = ((orders_all["日期"].dt.date >= start) & (orders_all["日期"].dt.date <= end)
        & orders_all["渠道"].isin(channels))
orders = orders_all[mask]
funnel = funnel_all[(funnel_all["日期"].dt.date >= start)
                    & (funnel_all["日期"].dt.date <= end)]

if orders.empty:
    st.warning("筛选条件下没有订单——放宽日期或渠道试试。")
    st.stop()

k = kpis(orders)
metric_row([
    {"label": "GMV·实付（万元）", "value": f"{k['gmv'] / 10000:,.1f}"},
    {"label": "订单数", "value": f"{k['orders']:,}"},
    {"label": "客单价（元）", "value": f"{k['aov']:,.0f}"},
    {"label": "复购率", "value": f"{k['repurchase_rate']:.1%}"},
    {"label": "退款率", "value": f"{k['refund_rate']:.1%}"},
])

_FREQ = {"按日": "D", "按周": "W", "按月": "M"}
_FUNNEL_COLORS = [tokens.SEQ_BLUE[i] for i in (3, 5, 7, 9, 11)]

g1, g2 = st.columns(2)
with g1:
    t = trend(orders, _FREQ[freq_label])
    fig = go.Figure(go.Bar(x=t["期"], y=t["GMV"] / 10000,
                           customdata=t["订单数"],
                           hovertemplate="%{x|%Y-%m-%d}<br>GMV %{y:,.1f} 万"
                                         "<br>订单 %{customdata} 单<extra></extra>"))
    fig.update_layout(title=f"GMV 趋势（{freq_label}，万元）", showlegend=False)
    st.plotly_chart(fig, width="stretch")
with g2:
    ft = funnel_totals(funnel)
    fig = go.Figure(go.Funnel(
        y=ft["环节"], x=ft["人数"], marker=dict(color=_FUNNEL_COLORS),
        texttemplate="%{value:,d}<br>%{percentPrevious:.0%}", textposition="auto",
        connector=dict(line=dict(color=tokens.GRID)),
    ))
    fig.update_layout(title="转化漏斗（全站，随日期筛选）")
    st.plotly_chart(fig, width="stretch")

g3, g4 = st.columns(2)
with g3:
    dim = st.radio("排行维度", ["类目", "SKU"], horizontal=True,
                   key="ec_dim", label_visibility="collapsed")
    rank = top_n(orders, dim, "实付金额")
    fig = go.Figure(go.Bar(x=rank["实付金额"] / 10000, y=rank[dim], orientation="h"))
    fig.update_layout(title=f"实付金额·按{dim} Top10（万元）", showlegend=False,
                      yaxis=dict(autorange="reversed"))
    st.plotly_chart(fig, width="stretch")
with g4:
    ch = orders.groupby("渠道", as_index=False)["实付金额"].sum() \
               .sort_values("实付金额", ascending=False)
    fig = go.Figure(go.Bar(x=ch["渠道"], y=ch["实付金额"] / 10000))
    fig.update_layout(title="GMV·按渠道（万元）", showlegend=False)
    st.plotly_chart(fig, width="stretch")

g5, g6 = st.columns(2)
with g5:
    freq_dist = purchase_freq_dist(orders)
    fig = go.Figure(go.Bar(x=freq_dist["购买次数"], y=freq_dist["用户数"],
                           marker_color=tokens.SERIES[2]))
    fig.update_layout(title="购买次数分布（用户数）", showlegend=False)
    st.plotly_chart(fig, width="stretch")
with g6:
    st.markdown("&nbsp;")
    excel_download_button(
        {"趋势": t, "排行": rank, "渠道": ch, "漏斗": ft}, "电商运营分析.xlsx")
    pdf_download_button(
        f"电商运营摘要（{start} ~ {end}）",
        [("GMV", f"¥{k['gmv'] / 10000:,.1f} 万"), ("订单数", f"{k['orders']:,}"),
         ("客单价", f"¥{k['aov']:,.0f}"), ("复购率", f"{k['repurchase_rate']:.1%}"),
         ("退款率", f"{k['refund_rate']:.1%}")],
        ["数据为程序生成的演示数据。GMV 含后续退款订单，净销售口径见明细。",
         "漏斗为全站数据，随日期筛选、不随渠道筛选。"],
        "电商运营摘要.pdf",
    )

st.caption("口径：GMV=实付合计（含后续退款单）；复购率=下单≥2次用户/购买用户；漏斗不随渠道筛选。")
