"""统一筛选器：日期范围与多选。"""

import datetime as dt

import streamlit as st


def date_range_filter(label: str, min_date: dt.date, max_date: dt.date, key: str):
    """返回 (start, end)；用户只选了一端时另一端取边界值。"""
    picked = st.date_input(
        label, value=(min_date, max_date),
        min_value=min_date, max_value=max_date, key=key,
    )
    if isinstance(picked, tuple) and len(picked) == 2:
        return picked[0], picked[1]
    if isinstance(picked, tuple) and len(picked) == 1:
        return picked[0], max_date
    return min_date, max_date


def multiselect_filter(label: str, options: list, key: str) -> list:
    """空选视为全选，返回生效的选项列表。"""
    picked = st.multiselect(label, options, default=None, key=key,
                            placeholder="全部（可多选筛选）")
    return picked if picked else list(options)
