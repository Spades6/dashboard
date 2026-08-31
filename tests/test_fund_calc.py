"""基金口径单测：python tests/test_fund_calc.py 直接运行（T1）。"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import numpy as np
import pandas as pd

from lib.fund_calc import (annualized_return, annualized_vol, dca_simulate,
                           drawdown_series, max_drawdown, period_return, rebase)


def test_rebase_and_return():
    nav = pd.Series([2.0, 2.2, 2.5])
    assert rebase(nav).tolist() == [1.0, 1.1, 1.25]
    assert period_return(nav) == 0.25


def test_max_drawdown():
    nav = pd.Series([1.0, 1.5, 0.9, 1.2, 1.8])
    assert max_drawdown(nav) == 0.9 / 1.5 - 1          # 峰 1.5 → 谷 0.9 = -40%
    dd = drawdown_series(nav)
    assert dd.iloc[0] == 0.0 and dd.iloc[-1] == 0.0    # 新高处回撤为 0


def test_annualized():
    # 250 个交易日翻倍 → 年化恰为 100%
    nav = pd.Series(np.linspace(1.0, 2.0, 251))
    assert abs(annualized_return(nav) - 1.0) < 1e-9
    # 恒定净值 → 波动为 0
    assert annualized_vol(pd.Series([1.0] * 100)) == 0.0


def test_dca_simulate():
    # 两个月，每月首个交易日净值 1.0 / 2.0，期末净值 2.0
    df = pd.DataFrame({
        "日期": ["2026-01-05", "2026-01-20", "2026-02-02", "2026-02-25"],
        "单位净值": [1.0, 1.5, 2.0, 2.0],
    })
    r = dca_simulate(df, 1000)
    assert r["months"] == 2
    assert r["invested"] == 2000
    # 份额 = 1000/1.0 + 1000/2.0 = 1500；市值 = 1500*2.0 = 3000
    assert r["value"] == 3000
    assert r["return_rate"] == 0.5


if __name__ == "__main__":
    test_rebase_and_return()
    test_max_drawdown()
    test_annualized()
    test_dca_simulate()
    print("ALL FUND CALC TESTS PASS")
