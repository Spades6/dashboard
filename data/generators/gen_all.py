"""一键生成全部演示数据（固定种子，可复现）：python data/generators/gen_all.py

schema 契约见 .ths/PROJECT.md。所有数据均为程序生成的假数据，
基金代码/名称为虚构，不对应任何真实产品。
"""

from pathlib import Path

import numpy as np
import pandas as pd

SEED = 42
OUT = Path(__file__).resolve().parent.parent / "samples"


def gen_finance_monthly(rng: np.random.Generator) -> pd.DataFrame:
    months = pd.period_range("2024-09", "2026-08", freq="M")
    n = len(months)
    t = np.arange(n)
    season = 1 + 0.12 * np.sin(2 * np.pi * (t + 2) / 12)  # Q4 旺季
    cny = np.array([0.82 if m.month == 2 else 1.0 for m in months])  # 春节低谷
    revenue = 8_000_000 * (1.02 ** t) * season * cny * rng.normal(1, 0.03, n)
    budget_rev = 8_200_000 * (1.02 ** t) * season  # 预算：无噪声的计划线
    cogs = revenue * rng.normal(0.55, 0.012, n)
    sales_exp = revenue * rng.normal(0.12, 0.008, n)
    admin_exp = 640_000 * (1.005 ** t) * rng.normal(1, 0.02, n)  # 管理费用黏性
    rd_exp = revenue * rng.normal(0.06, 0.004, n)
    other = rng.normal(30_000, 15_000, n)
    cash_in = np.roll(revenue, 1) * 0.15 + revenue * 0.85  # 部分回款滞后一月
    cash_in[0] = revenue[0] * 0.9
    cash_out = cogs * 0.95 + sales_exp + admin_exp + rd_exp
    return pd.DataFrame({
        "月份": months.astype(str),
        "营收": revenue.round(0).astype(int),
        "营业成本": cogs.round(0).astype(int),
        "销售费用": sales_exp.round(0).astype(int),
        "管理费用": admin_exp.round(0).astype(int),
        "研发费用": rd_exp.round(0).astype(int),
        "其他收益": other.round(0).astype(int),
        "预算营收": budget_rev.round(0).astype(int),
        "预算净利润": (budget_rev * 0.13).round(0).astype(int),
        "经营现金流入": cash_in.round(0).astype(int),
        "经营现金流出": cash_out.round(0).astype(int),
    })


_CATS = {
    "女装": (35, 89, 299), "男装": (25, 99, 349), "美妆": (20, 59, 499),
    "家居": (15, 29, 199), "数码": (10, 199, 2999),
}


def gen_ecom(rng: np.random.Generator) -> tuple[pd.DataFrame, pd.DataFrame]:
    days = pd.date_range("2025-09-01", "2026-08-31", freq="D")
    boost = np.ones(len(days))
    for i, d in enumerate(days):
        if (d.month, d.day) in [(11, 11), (11, 10), (6, 18), (6, 17), (12, 12)]:
            boost[i] = 4.2 if d.day in (11, 18) else 2.2  # 大促
        elif d.weekday() >= 5:
            boost[i] = 1.25
    day_w = boost / boost.sum()

    n = 5000
    skus, prices, cats = [], [], []
    for cat, (cnt, lo, hi) in _CATS.items():
        for i in range(cnt):
            skus.append(f"{cat}-{i + 1:03d}")
            prices.append(round(float(rng.uniform(lo, hi)), -1) + 9)  # x9 定价
            cats.append(cat)
    sku_w = rng.dirichlet(np.full(len(skus), 0.6))  # 头部集中
    idx = rng.choice(len(skus), n, p=sku_w)
    user_pool = rng.choice(np.arange(10001, 12001), 2000, replace=False)
    user_w = rng.dirichlet(np.full(2000, 0.35))  # 少数用户高复购
    qty = rng.choice([1, 1, 1, 2, 2, 3], n)
    price = np.array(prices)[idx]
    paid = price * qty * rng.uniform(0.85, 1.0, n)
    orders = pd.DataFrame({
        "订单号": [f"SO{202500000 + i}" for i in range(n)],
        "日期": rng.choice(days, n, p=day_w),
        "用户ID": rng.choice(user_pool, n, p=user_w),
        "渠道": rng.choice(["直播", "搜索", "推荐", "社群"], n, p=[0.35, 0.3, 0.2, 0.15]),
        "类目": np.array(cats)[idx],
        "SKU": np.array(skus)[idx],
        "数量": qty,
        "单价": price.astype(int),
        "实付金额": paid.round(2),
        "是否退款": rng.choice(["否", "是"], n, p=[0.94, 0.06]),
    }).sort_values("日期").reset_index(drop=True)

    # 漏斗从订单日计数反推：跨表一致，且逐层放大保证单调
    paid_n = orders.groupby("日期").size().reindex(days, fill_value=0).to_numpy()
    placed = np.maximum((paid_n / rng.normal(0.80, 0.03, len(days))).astype(int), paid_n)
    carts = np.maximum((placed / rng.normal(0.40, 0.03, len(days))).astype(int), placed)
    views = np.maximum((carts / rng.normal(0.32, 0.02, len(days))).astype(int), carts)
    visitors = np.maximum((views / rng.normal(0.55, 0.03, len(days))).astype(int), views)
    funnel = pd.DataFrame({"日期": days, "访客数": visitors, "商品浏览": views,
                           "加购": carts, "下单": placed, "支付": paid_n})
    return orders, funnel


_FUNDS = [  # 虚构代码与名称
    ("F30021", "蓝筹增强A", 0.05, 0.18),
    ("F11005", "稳健纯债C", 0.035, 0.04),
    ("F77012", "全球科技先锋", 0.12, 0.28),
]


def gen_fund_nav(rng: np.random.Generator) -> pd.DataFrame:
    days = pd.bdate_range("2023-09-01", "2026-08-31")
    frames = []
    for code, name, drift, vol in _FUNDS:
        dt = 1 / 250
        rets = rng.normal((drift - vol ** 2 / 2) * dt, vol * np.sqrt(dt), len(days))
        nav = np.exp(np.cumsum(rets))
        frames.append(pd.DataFrame({"日期": days, "基金代码": code, "基金名称": name,
                                    "单位净值": nav.round(4)}))
    return pd.concat(frames, ignore_index=True)


_DEPTS = ["技术", "产品", "销售", "市场", "职能", "客服"]
_BANDS = {1: "6-10k", 2: "10-15k", 3: "15-25k", 4: "25-35k", 5: "35-50k", 6: "50k+"}


def gen_hr(rng: np.random.Generator) -> tuple[pd.DataFrame, pd.DataFrame]:
    n = 380
    dept = rng.choice(_DEPTS, n, p=[0.32, 0.10, 0.22, 0.08, 0.12, 0.16])
    age = np.clip(rng.normal(31, 6, n), 22, 58).astype(int)
    tenure = np.minimum(np.round(rng.exponential(2.5, n), 1), age - 22)
    level = rng.choice([1, 2, 3, 4, 5, 6], n, p=[0.10, 0.28, 0.32, 0.18, 0.09, 0.03])
    leave_p = np.where(np.isin(dept, ["销售", "客服"]), 0.18, 0.09)
    roster = pd.DataFrame({
        "工号": [f"E{1001 + i}" for i in range(n)],
        "部门": dept,
        "性别": rng.choice(["男", "女"], n, p=[0.55, 0.45]),
        "年龄": age,
        "司龄": tenure,
        "职级": [f"P{lv}" for lv in level],
        "月薪档": [_BANDS[lv] for lv in level],
        "在职状态": np.where(rng.random(n) < leave_p, "本年离职", "在职"),
    })

    m = 260
    s_dept = rng.choice(_DEPTS, m, p=[0.30, 0.10, 0.20, 0.08, 0.14, 0.18])
    base = {"技术": 3.9, "产品": 3.7, "销售": 3.3, "市场": 3.6, "职能": 3.8, "客服": 3.1}
    mu = np.array([base[d] for d in s_dept])

    def score(shift=0.0):
        return np.clip(np.round(rng.normal(mu + shift, 0.7)), 1, 5).astype(int)

    survey = pd.DataFrame({
        "问卷ID": [f"Q{5001 + i}" for i in range(m)],
        "部门": s_dept,
        "敬业度": score(),
        "薪酬满意度": score(-0.5),
        "管理满意度": score(-0.1),
        "成长满意度": score(0.1),
        "工作生活平衡": score(-0.3),
        "NPS": np.clip(np.round(rng.normal(mu * 2, 2.2)), 0, 10).astype(int),
    })
    return roster, survey


_REGIONS = {"华东": ["上海", "杭州", "南京"], "华北": ["北京", "天津"],
            "华南": ["深圳", "广州"], "西南": ["成都", "重庆"], "华中": ["武汉", "长沙"]}
_LINES = {"标准版": 0.42, "专业版": 0.55, "旗舰版": 0.62, "配件": 0.35}


def gen_generic_sales(rng: np.random.Generator) -> pd.DataFrame:
    n = 1000
    regions = rng.choice(list(_REGIONS), n, p=[0.34, 0.2, 0.22, 0.13, 0.11])
    cities = [rng.choice(_REGIONS[r]) for r in regions]
    lines = rng.choice(list(_LINES), n, p=[0.4, 0.3, 0.15, 0.15])
    amount = rng.lognormal(9.2, 0.7, n)
    margin = np.array([_LINES[ln] for ln in lines])
    return pd.DataFrame({
        "日期": rng.choice(pd.date_range("2025-09-01", "2026-08-31"), n),
        "区域": regions,
        "城市": cities,
        "产品线": lines,
        "销售额": amount.round(2),
        "销量": np.maximum((amount / rng.uniform(800, 3000, n)).astype(int), 1),
        "毛利": (amount * margin * rng.normal(1, 0.05, n)).round(2),
    }).sort_values("日期").reset_index(drop=True)


def main() -> None:
    rng = np.random.default_rng(SEED)
    OUT.mkdir(parents=True, exist_ok=True)
    outputs = {"finance_monthly.csv": gen_finance_monthly(rng)}
    outputs["ecom_orders.csv"], outputs["ecom_funnel.csv"] = gen_ecom(rng)
    outputs["fund_nav.csv"] = gen_fund_nav(rng)
    outputs["hr_roster.csv"], outputs["hr_survey.csv"] = gen_hr(rng)
    outputs["generic_sales.csv"] = gen_generic_sales(rng)
    for name, df in outputs.items():
        df.to_csv(OUT / name, index=False, encoding="utf-8-sig")
        print(f"{name}: {len(df)} 行")


if __name__ == "__main__":
    main()
