"""假数据生成测试：python tests/test_data.py 直接运行（T1）。"""

import hashlib
import subprocess
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
SAMPLES = ROOT / "data" / "samples"

EXPECTED = {
    "finance_monthly.csv": ["月份", "营收", "营业成本", "销售费用", "管理费用", "研发费用",
                            "其他收益", "预算营收", "预算净利润", "经营现金流入", "经营现金流出"],
    "ecom_orders.csv": ["订单号", "日期", "用户ID", "渠道", "类目", "SKU", "数量",
                        "单价", "实付金额", "是否退款"],
    "ecom_funnel.csv": ["日期", "访客数", "商品浏览", "加购", "下单", "支付"],
    "fund_nav.csv": ["日期", "基金代码", "基金名称", "单位净值"],
    "hr_roster.csv": ["工号", "部门", "性别", "年龄", "司龄", "职级", "月薪档", "在职状态"],
    "hr_survey.csv": ["问卷ID", "部门", "敬业度", "薪酬满意度", "管理满意度",
                      "成长满意度", "工作生活平衡", "NPS"],
    "generic_sales.csv": ["日期", "区域", "城市", "产品线", "销售额", "销量", "毛利"],
}


def run_gen() -> dict[str, str]:
    subprocess.run([sys.executable, str(ROOT / "data" / "generators" / "gen_all.py")],
                   check=True, capture_output=True)
    return {f: hashlib.sha256((SAMPLES / f).read_bytes()).hexdigest() for f in EXPECTED}


def test_all():
    h1 = run_gen()
    for fname, cols in EXPECTED.items():
        df = pd.read_csv(SAMPLES / fname)
        assert list(df.columns) == cols, f"{fname} 列不符: {list(df.columns)}"
        assert len(df) > 20, f"{fname} 行数过少"
    # 量纲与业务合理性抽查
    fin = pd.read_csv(SAMPLES / "finance_monthly.csv")
    assert len(fin) == 24
    assert (fin["营收"] > fin["营业成本"]).all(), "营收应大于营业成本"
    funnel = pd.read_csv(SAMPLES / "ecom_funnel.csv")
    assert ((funnel["访客数"] >= funnel["商品浏览"]) & (funnel["商品浏览"] >= funnel["加购"])
            & (funnel["加购"] >= funnel["下单"]) & (funnel["下单"] >= funnel["支付"])).all(), \
        "漏斗必须单调递减"
    nav = pd.read_csv(SAMPLES / "fund_nav.csv")
    assert nav["基金代码"].nunique() == 3 and (nav["单位净值"] > 0).all()
    nav_dates = pd.to_datetime(nav["日期"])
    assert nav_dates.min() >= pd.Timestamp("2023-09-01")
    assert nav_dates.max() <= pd.Timestamp("2026-08-31")
    assert (nav_dates.dt.weekday < 5).all(), "基金净值只应有交易日"
    orders = pd.read_csv(SAMPLES / "ecom_orders.csv")
    assert funnel["支付"].sum() == len(orders), "漏斗支付总数必须等于订单明细行数"
    roster = pd.read_csv(SAMPLES / "hr_roster.csv")
    assert (roster["司龄"] <= roster["年龄"] - 22).all(), "司龄不得超过 年龄-22"
    # 可复现性：重跑一遍字节级一致
    h2 = run_gen()
    assert h1 == h2, "固定种子下重跑结果应完全一致"


if __name__ == "__main__":
    test_all()
    print("ALL DATA TESTS PASS")
