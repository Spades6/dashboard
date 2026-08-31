"""指标卡行。item: {label, value, delta(可选, 带符号字符串), good(可选, 增量方向是否向好)}"""

import html

import streamlit as st


def metric_row(items: list[dict]) -> None:
    cols = st.columns(len(items))
    for col, item in zip(cols, items):
        delta_html = ""
        delta = item.get("delta")
        if delta is not None:
            good = item.get("good")
            cls = "flat" if good is None else ("good" if good else "bad")
            delta_html = f'<div class="m-delta {cls}">{html.escape(str(delta))}</div>'
        col.markdown(
            f'<div class="spade-metric">'
            f'<div class="m-label">{html.escape(str(item["label"]))}</div>'
            f'<div class="m-value">{html.escape(str(item["value"]))}</div>'
            f"{delta_html}</div>",
            unsafe_allow_html=True,
        )
