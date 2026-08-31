"""财务经营分析的纯计算逻辑（口径见 tests/test_finance_calc.py）。金额列单位：元。"""

import pandas as pd

EXPENSE_COLS = ["销售费用", "管理费用", "研发费用"]


def enrich(df: pd.DataFrame) -> pd.DataFrame:
    """追加派生列：净利润、毛利率、净利率、预算达成率、净现金流、同比、环比。"""
    out = df.copy()
    out["净利润"] = (out["营收"] - out["营业成本"] - out[EXPENSE_COLS].sum(axis=1)
                     + out["其他收益"])
    out["毛利率"] = (out["营收"] - out["营业成本"]) / out["营收"]
    out["净利率"] = out["净利润"] / out["营收"]
    out["预算达成率"] = out["营收"] / out["预算营收"]
    out["净现金流"] = out["经营现金流入"] - out["经营现金流出"]
    out["营收环比"] = out["营收"].pct_change()
    out["营收同比"] = out["营收"].pct_change(12)
    out["净利润环比"] = out["净利润"].pct_change()
    out["净利润同比"] = out["净利润"].pct_change(12)
    return out


def window_kpis(enriched: pd.DataFrame, start: str, end: str) -> dict:
    """所选月份区间的 KPI 汇总，delta 对比前一个等长区间（不足等长则无 delta）。

    比率口径为区间加权（合计口径），非各月简单平均。
    """
    months = enriched["月份"].tolist()
    i0, i1 = months.index(start), months.index(end)
    cur = enriched.iloc[i0:i1 + 1]
    n = len(cur)
    prev = enriched.iloc[i0 - n:i0] if i0 - n >= 0 else None

    def agg(w: pd.DataFrame) -> dict:
        return {
            "营收": w["营收"].sum(),
            "净利润": w["净利润"].sum(),
            "净利率": w["净利润"].sum() / w["营收"].sum(),
            "预算达成率": w["营收"].sum() / w["预算营收"].sum(),
        }

    kpis = {"n": n, "cur": agg(cur)}
    kpis["prev"] = agg(prev) if prev is not None and len(prev) == n else None
    return kpis


def fmt_wan(x: float) -> str:
    """元 → 「x,xxx 万」。"""
    return f"{x / 10000:,.0f} 万"


def fmt_pct(x: float, signed: bool = False) -> str:
    return f"{x:+.1%}" if signed else f"{x:.1%}"


def fmt_pp(x: float) -> str:
    """百分点差，带符号。"""
    return f"{x * 100:+.1f}pp"
