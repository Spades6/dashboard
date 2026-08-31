"""字段识别单测：python tests/test_auto_profile.py 直接运行（T1）。"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pandas as pd

from lib.auto_profile import monthly_trend, profile, top_n


def test_profile():
    df = pd.DataFrame({
        "订单号": range(100),                       # 整数高唯一 → ID
        "日期": ["2026-01-0" + str(i % 9 + 1) for i in range(100)],  # 文本日期
        "区域": ["华东", "华北"] * 50,               # 低基数分类
        "备注": [f"备注{i}" for i in range(100)],    # 文本高唯一 → ID
        "金额": [100.5] * 100,                      # 数值
    })
    p = profile(df)
    assert p["date"] == ["日期"]
    assert p["numeric"] == ["金额"]
    assert p["category"] == ["区域"]
    assert set(p["id"]) == {"订单号", "备注"}
    assert p["rows"] == 100


def test_profile_datetime_dtype():
    df = pd.DataFrame({"d": pd.date_range("2026-01-01", periods=5), "v": [1, 2, 3, 4, 5]})
    p = profile(df)
    assert p["date"] == ["d"]
    assert p["numeric"] == ["v"]   # 低唯一占比整数不是 ID


def test_monthly_trend():
    df = pd.DataFrame({"d": ["2026-01-05", "2026-01-20", "2026-02-01"], "v": [1, 2, 4]})
    t = monthly_trend(df, "d", "v")
    assert t["v"].tolist() == [3, 4]
    assert t["月份"].tolist() == ["2026-01", "2026-02"]


def test_top_n():
    df = pd.DataFrame({"c": list("abcde"), "v": [5, 4, 3, 2, 1]})
    t = top_n(df, "c", "v", n=3)
    assert t["c"].tolist() == ["a", "b", "c", "其他"]
    assert t["v"].tolist() == [5, 4, 3, 3]


if __name__ == "__main__":
    test_profile()
    test_profile_datetime_dtype()
    test_monthly_trend()
    test_top_n()
    print("ALL AUTO PROFILE TESTS PASS")
