"""电商口径单测：python tests/test_ecom_calc.py 直接运行（T1）。"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pandas as pd

from lib.ecom_calc import funnel_totals, kpis, purchase_freq_dist, trend


def make_orders():
    # 4 单 3 用户：u1 两单(其中1退款), u2/u3 各一单
    return pd.DataFrame({
        "订单号": ["A1", "A2", "A3", "A4"],
        "日期": ["2026-01-01", "2026-01-02", "2026-01-02", "2026-02-01"],
        "用户ID": [1, 1, 2, 3],
        "实付金额": [100.0, 200.0, 300.0, 400.0],
        "是否退款": ["否", "是", "否", "否"],
    })


def test_kpis():
    k = kpis(make_orders())
    assert k["gmv"] == 1000.0
    assert k["net_sales"] == 800.0            # 剔除 200 退款
    assert k["orders"] == 4
    assert k["aov"] == 250.0
    assert k["repurchase_rate"] == 1 / 3       # 仅 u1 复购
    assert k["refund_rate"] == 0.25
    empty = kpis(make_orders().iloc[0:0])
    assert empty["orders"] == 0 and empty["aov"] is None


def test_trend():
    t = trend(make_orders(), "M")
    assert t["GMV"].tolist() == [600.0, 400.0]
    assert t["订单数"].tolist() == [3, 1]


def test_funnel_totals():
    f = pd.DataFrame({"访客数": [100, 100], "商品浏览": [60, 60], "加购": [20, 20],
                      "下单": [10, 10], "支付": [8, 8]})
    ft = funnel_totals(f)
    assert ft["人数"].tolist() == [200, 120, 40, 20, 16]
    assert ft["转化率"].iloc[1] == 0.6
    assert ft["转化率"].iloc[4] == 0.8
    assert pd.isna(ft["转化率"].iloc[0])      # None 入 float 列成 NaN


def test_purchase_freq_dist():
    d = purchase_freq_dist(make_orders())
    assert d["用户数"].tolist() == [2, 1, 0]   # u2/u3 一次, u1 两次, 无 3+


if __name__ == "__main__":
    test_kpis()
    test_trend()
    test_funnel_totals()
    test_purchase_freq_dist()
    print("ALL ECOM CALC TESTS PASS")
