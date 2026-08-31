"""HR 口径单测：python tests/test_hr_calc.py 直接运行（T1）。"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pandas as pd

from lib.hr_calc import attrition_by_dept, nps, satisfaction_matrix


def test_nps():
    # 10 人：3 推荐(9,9,10) 4 中立(7,7,8,8) 3 贬损(6,5,0) → (3-3)/10 = 0
    assert nps(pd.Series([9, 9, 10, 7, 7, 8, 8, 6, 5, 0])) == 0.0
    assert nps(pd.Series([10, 10, 9, 8])) == 0.75
    assert nps(pd.Series([], dtype=int)) == 0.0


def test_attrition():
    roster = pd.DataFrame({
        "部门": ["技术", "技术", "技术", "销售", "销售"],
        "在职状态": ["在职", "在职", "本年离职", "在职", "本年离职"],
    })
    a = attrition_by_dept(roster).set_index("部门")
    assert a.loc["技术", "在职人数"] == 2
    assert a.loc["技术", "离职率"] == 1 / 3
    assert a.loc["销售", "离职率"] == 1 / 2


def test_satisfaction_matrix():
    survey = pd.DataFrame({
        "部门": ["技术", "技术", "销售"],
        "敬业度": [4, 5, 3], "薪酬满意度": [3, 3, 2], "管理满意度": [4, 4, 3],
        "成长满意度": [5, 4, 3], "工作生活平衡": [3, 4, 2],
    })
    m = satisfaction_matrix(survey)
    assert m.loc["技术", "敬业度"] == 4.5
    assert m.loc["销售", "薪酬满意度"] == 2.0
    assert list(m.columns) == ["敬业度", "薪酬满意度", "管理满意度", "成长满意度", "工作生活平衡"]


if __name__ == "__main__":
    test_nps()
    test_attrition()
    test_satisfaction_matrix()
    print("ALL HR CALC TESTS PASS")
