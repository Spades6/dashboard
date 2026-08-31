from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from components.export import excel_download_button
from components.layout import page_header, setup_page
from components.metrics import metric_row
from lib.auto_profile import monthly_trend, profile, top_n

setup_page("Excel 一键变看板", "⚡")
page_header(
    "⚡ Excel 一键变看板",
    "上传 Excel/CSV，自动识别日期、指标和维度字段，30 秒生成能筛、能导出的看板——"
    "不用写公式，不用配置。",
)
st.info("🔒 你上传的数据只在当前会话的内存中处理，不写入磁盘、不留存，刷新页面即消失。", icon="🔒")

_DEMO = Path(__file__).resolve().parent.parent / "data" / "samples" / "generic_sales.csv"


def _read_upload(file) -> pd.DataFrame:
    if file.name.lower().endswith(".csv"):
        try:
            return pd.read_csv(file)
        except UnicodeDecodeError:
            file.seek(0)
            return pd.read_csv(file, encoding="gb18030")
    return pd.read_excel(file)


up = st.file_uploader("上传 Excel (.xlsx) 或 CSV", type=["xlsx", "csv"], key="up1")
if up is not None:
    try:
        df = _read_upload(up)
    except Exception as e:
        st.error(f"文件无法读取（{e.__class__.__name__}）。请确认是标准的 .xlsx 或 CSV 文件，"
                 "带一行表头、每列一个字段。")
        st.stop()
    if df.empty:
        st.warning("文件读出来是空的——请检查后重新上传。")
        st.stop()
    st.caption(f"已读取 **{up.name}**（{len(df)} 行）")
else:
    df = pd.read_csv(_DEMO)
    st.caption("当前展示**演示数据**（程序生成的销售明细）——上传你的文件即刻替换。")

prof = profile(df)
if not prof["numeric"]:
    st.warning("没有识别到数值列，无法生成图表。请确认表内至少有一列数字。")
    st.dataframe(df.head(50), width="stretch")
    st.stop()

c1, c2, c3 = st.columns(3)
value_col = c1.selectbox("指标列", prof["numeric"], key="up_val")
date_col = c2.selectbox("日期列", ["（无）", *prof["date"]],
                        index=1 if prof["date"] else 0, key="up_date")
cat_col = c3.selectbox("维度列", ["（无）", *prof["category"]],
                       index=1 if prof["category"] else 0, key="up_cat")


def _fmt(x: float) -> str:
    if abs(x) >= 1e8:
        return f"{x / 1e8:,.2f} 亿"
    if abs(x) >= 1e4:
        return f"{x / 1e4:,.1f} 万"
    return f"{x:,.1f}"


kpis = [
    {"label": "数据行数", "value": f"{prof['rows']:,}"},
    {"label": f"{value_col}·合计", "value": _fmt(df[value_col].sum())},
    {"label": f"{value_col}·单行均值", "value": _fmt(df[value_col].mean())},
]
bad_dates = 0
if date_col != "（无）":
    d = pd.to_datetime(df[date_col], errors="coerce", format="mixed")
    bad_dates = int(d.isna().sum())
    kpis.append({"label": "时间跨度",
                 "value": f"{d.min():%Y-%m-%d} ~ {d.max():%Y-%m-%d}"})
metric_row(kpis)
if bad_dates:
    st.caption(f"⚠️ {bad_dates} 行的「{date_col}」无法解析为日期，趋势图已跳过这些行。")

exports: dict[str, pd.DataFrame] = {}
g1, g2 = st.columns(2)
if date_col != "（无）":
    trend = monthly_trend(df, date_col, value_col)
    exports["月度趋势"] = trend
    with g1:
        fig = go.Figure(go.Bar(x=trend["月份"], y=trend[value_col]))
        fig.update_layout(title=f"{value_col}·月度合计", showlegend=False)
        fig.update_xaxes(tickformat="%Y-%m")
        st.plotly_chart(fig, width="stretch")
if cat_col != "（无）":
    rank = top_n(df, cat_col, value_col)
    exports[f"{cat_col}排行"] = rank
    with (g2 if date_col != "（无）" else g1):
        fig = go.Figure(go.Bar(x=rank[value_col], y=rank[cat_col], orientation="h"))
        fig.update_layout(title=f"{value_col}·按{cat_col} Top10",
                          showlegend=False,
                          yaxis=dict(autorange="reversed"))
        st.plotly_chart(fig, width="stretch")
if not exports:
    st.warning("没有识别到日期列或维度列——仍可在下方查看明细。选择其他文件试试。")

with st.expander("明细预览（前 100 行）", expanded=False):
    st.dataframe(df.head(100), width="stretch", hide_index=True)

if exports:
    excel_download_button(exports, "一键看板聚合结果.xlsx", label="⬇️ 导出聚合结果 Excel")

st.caption("识别规则：日期列按可解析比例判定；高唯一占比的编号列自动排除；维度列取低基数文本列。")
