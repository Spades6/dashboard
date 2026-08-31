"""电商运营口径（见 tests/test_ecom_calc.py）。orders 列契约见 .ths/PROJECT.md。"""

import pandas as pd


def kpis(orders: pd.DataFrame) -> dict:
    """GMV=实付合计（含后续退款单）；净销售=剔除退款；客单价=GMV/订单数；
    复购率=下单≥2次用户/购买用户；退款率=退款单数/订单数。空表返回 None 值。"""
    n = len(orders)
    if n == 0:
        return {"gmv": 0.0, "orders": 0, "aov": None,
                "repurchase_rate": None, "refund_rate": None, "net_sales": 0.0}
    refunded = orders["是否退款"] == "是"
    per_user = orders.groupby("用户ID").size()
    return {
        "gmv": float(orders["实付金额"].sum()),
        "net_sales": float(orders.loc[~refunded, "实付金额"].sum()),
        "orders": n,
        "aov": float(orders["实付金额"].sum() / n),
        "repurchase_rate": float((per_user >= 2).sum() / len(per_user)),
        "refund_rate": float(refunded.sum() / n),
    }


def trend(orders: pd.DataFrame, freq: str) -> pd.DataFrame:
    """按 D/W/M 聚合 GMV 与订单数，返回列 [期, GMV, 订单数]。"""
    d = pd.to_datetime(orders["日期"])
    g = (orders.assign(期=d.dt.to_period(freq).dt.start_time)
               .groupby("期")
               .agg(GMV=("实付金额", "sum"), 订单数=("订单号", "count"))
               .reset_index())
    return g.sort_values("期")


def funnel_totals(funnel: pd.DataFrame) -> pd.DataFrame:
    """漏斗各层合计与相邻层转化率，返回列 [环节, 人数, 转化率]（首层转化率为 None）。"""
    stages = ["访客数", "商品浏览", "加购", "下单", "支付"]
    vals = [int(funnel[s].sum()) for s in stages]
    rates = [None] + [vals[i] / vals[i - 1] if vals[i - 1] else None
                      for i in range(1, len(vals))]
    return pd.DataFrame({"环节": stages, "人数": vals, "转化率": rates})


def purchase_freq_dist(orders: pd.DataFrame) -> pd.DataFrame:
    """购买用户按下单次数分桶（1 次 / 2 次 / 3 次及以上）。"""
    per_user = orders.groupby("用户ID").size()
    buckets = pd.cut(per_user, bins=[0, 1, 2, float("inf")],
                     labels=["1 次", "2 次", "3 次及以上"])
    out = buckets.value_counts().reindex(["1 次", "2 次", "3 次及以上"]).reset_index()
    out.columns = ["购买次数", "用户数"]
    return out
