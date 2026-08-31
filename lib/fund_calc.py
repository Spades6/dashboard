"""基金回测口径（见 tests/test_fund_calc.py）。nav 为按日期升序的单位净值序列。"""

import numpy as np
import pandas as pd

TRADING_DAYS = 250


def rebase(nav: pd.Series) -> pd.Series:
    """归一到区间起点=1。"""
    return nav / nav.iloc[0]


def period_return(nav: pd.Series) -> float:
    return float(nav.iloc[-1] / nav.iloc[0] - 1)


def annualized_return(nav: pd.Series) -> float:
    """按交易日数年化的几何收益。"""
    n = len(nav) - 1
    if n <= 0:
        return 0.0
    return float((nav.iloc[-1] / nav.iloc[0]) ** (TRADING_DAYS / n) - 1)


def annualized_vol(nav: pd.Series) -> float:
    return float(nav.pct_change().dropna().std(ddof=1) * np.sqrt(TRADING_DAYS))


def max_drawdown(nav: pd.Series) -> float:
    """最大回撤，返回负数（如 -0.23）。"""
    return float((nav / nav.cummax() - 1).min())


def drawdown_series(nav: pd.Series) -> pd.Series:
    return nav / nav.cummax() - 1


def dca_simulate(df: pd.DataFrame, monthly_amount: float) -> dict:
    """定投模拟：每月首个交易日按当日净值买入 monthly_amount 元。
    df 需含列 [日期, 单位净值]；函数内部按日期排序，不依赖输入顺序。"""
    d = (df.assign(_日=pd.to_datetime(df["日期"]))
           .sort_values("_日")
           .assign(_月=lambda x: x["_日"].dt.to_period("M")))
    first = d.groupby("_月", as_index=False).first()
    units = float((monthly_amount / first["单位净值"]).sum())
    invested = monthly_amount * len(first)
    value = units * float(d["单位净值"].iloc[-1])
    return {
        "months": len(first),
        "invested": float(invested),
        "value": value,
        "return_rate": value / invested - 1 if invested else 0.0,
    }
