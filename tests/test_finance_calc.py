"""财务口径单测：python tests/test_finance_calc.py 直接运行（T1）。"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pandas as pd

from lib.finance_calc import enrich, fmt_pp, fmt_pct, fmt_wan, window_kpis


def make_df():
    # 两个月手算样例：口径 净利润 = 营收-营业成本-三费+其他收益
    return pd.DataFrame({
        "月份": ["2026-01", "2026-02"],
        "营收": [1000.0, 1200.0],
        "营业成本": [550.0, 660.0],
        "销售费用": [120.0, 130.0],
        "管理费用": [80.0, 80.0],
        "研发费用": [50.0, 60.0],
        "其他收益": [10.0, 0.0],
        "预算营收": [1100.0, 1150.0],
        "预算净利润": [150.0, 160.0],
        "经营现金流入": [900.0, 1100.0],
        "经营现金流出": [800.0, 950.0],
    })


def test_enrich():
    e = enrich(make_df())
    assert e["净利润"].tolist() == [210.0, 270.0]          # 1000-550-250+10 / 1200-660-270+0
    assert e["毛利率"].tolist() == [0.45, 0.45]
    assert e["净利率"].tolist() == [0.21, 0.225]
    assert e["净现金流"].tolist() == [100.0, 150.0]
    assert round(e["营收环比"].iloc[1], 4) == 0.2
    assert pd.isna(e["营收同比"]).all()                     # 不足 12 期无同比


def test_window_kpis():
    e = enrich(make_df())
    k = window_kpis(e, "2026-02", "2026-02")
    assert k["n"] == 1 and k["cur"]["营收"] == 1200.0
    assert k["prev"]["营收"] == 1000.0                      # 前一等长区间
    k2 = window_kpis(e, "2026-01", "2026-02")
    assert k2["cur"]["净利润"] == 480.0
    assert k2["cur"]["净利率"] == 480.0 / 2200.0            # 加权而非平均
    assert k2["prev"] is None                               # 前面不足两个月


def test_fmt():
    assert fmt_wan(12840000) == "1,284 万"
    assert fmt_pct(0.186) == "18.6%"
    assert fmt_pct(0.124, signed=True) == "+12.4%"
    assert fmt_pp(-0.008) == "-0.8pp"


if __name__ == "__main__":
    test_enrich()
    test_window_kpis()
    test_fmt()
    print("ALL FINANCE CALC TESTS PASS")
