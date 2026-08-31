"""HR/问卷口径（见 tests/test_hr_calc.py）。"""

import pandas as pd

SURVEY_DIMS = ["敬业度", "薪酬满意度", "管理满意度", "成长满意度", "工作生活平衡"]


def nps(scores: pd.Series) -> float:
    """NPS = 推荐者(9-10)占比 − 贬损者(0-6)占比，范围 [-1, 1]。"""
    n = len(scores)
    if n == 0:
        return 0.0
    promoters = (scores >= 9).sum()
    detractors = (scores <= 6).sum()
    return float((promoters - detractors) / n)


def attrition_by_dept(roster: pd.DataFrame) -> pd.DataFrame:
    """按部门统计：在职人数、本年离职数、离职率=离职/(在职+离职)。"""
    g = roster.groupby("部门")["在职状态"]
    out = pd.DataFrame({
        "在职人数": g.apply(lambda s: int((s == "在职").sum())),
        "本年离职": g.apply(lambda s: int((s == "本年离职").sum())),
    }).reset_index()
    out["离职率"] = out["本年离职"] / (out["在职人数"] + out["本年离职"])
    return out.sort_values("在职人数", ascending=False)


def satisfaction_matrix(survey: pd.DataFrame) -> pd.DataFrame:
    """部门 × 五维满意度均值矩阵（行=部门，列=维度）。"""
    return survey.groupby("部门")[SURVEY_DIMS].mean().round(2)
