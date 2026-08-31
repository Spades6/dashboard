"""上传表格的字段自动识别（纯逻辑，见 tests/test_auto_profile.py）。"""

import pandas as pd

MAX_CAT_UNIQUE = 30       # 分类列的唯一值上限
ID_UNIQUE_RATIO = 0.95    # 唯一值占比超过此值视为 ID 列（不作指标/维度）
ID_MIN_UNIQUE = 20        # 唯一值太少时不判 ID（小表全唯一很常见）
DATE_PARSE_RATIO = 0.9    # 文本列可解析为日期的比例阈值


def _is_id_like(s: pd.Series) -> bool:
    return s.nunique() >= ID_MIN_UNIQUE and s.nunique() / len(s) > ID_UNIQUE_RATIO


def profile(df: pd.DataFrame) -> dict:
    """返回 {"date": [...], "numeric": [...], "category": [...], "id": [...]}。"""
    date_cols, numeric_cols, cat_cols, id_cols = [], [], [], []
    n = len(df)
    for col in df.columns:
        s = df[col].dropna()
        if s.empty:
            continue
        if pd.api.types.is_datetime64_any_dtype(s):
            date_cols.append(col)
            continue
        if pd.api.types.is_numeric_dtype(s):
            # 高唯一占比的整数列（订单号/工号等）视为 ID
            if pd.api.types.is_integer_dtype(s) and _is_id_like(s):
                id_cols.append(col)
            else:
                numeric_cols.append(col)
            continue
        # 文本列：先试日期（抽样探测，防大表全量解析），再看是否低基数分类
        parsed = pd.to_datetime(s.iloc[:1000], errors="coerce", format="mixed")
        if parsed.notna().mean() >= DATE_PARSE_RATIO:
            date_cols.append(col)
        elif s.nunique() <= MAX_CAT_UNIQUE:
            cat_cols.append(col)
        elif _is_id_like(s):
            id_cols.append(col)
    return {"date": date_cols, "numeric": numeric_cols,
            "category": cat_cols, "id": id_cols, "rows": n}


def monthly_trend(df: pd.DataFrame, date_col: str, value_col: str) -> pd.DataFrame:
    """按月聚合数值列合计，返回列 [月份, value_col]。"""
    d = pd.to_datetime(df[date_col], errors="coerce", format="mixed")
    out = (df.assign(月份=d.dt.to_period("M").astype(str))
             .dropna(subset=["月份"])
             .groupby("月份", as_index=False)[value_col].sum())
    return out.sort_values("月份")


def top_n(df: pd.DataFrame, cat_col: str, value_col: str, n: int = 10) -> pd.DataFrame:
    """维度 TopN 合计，其余归入「其他」。"""
    g = df.groupby(cat_col, as_index=False)[value_col].sum() \
          .sort_values(value_col, ascending=False)
    if len(g) <= n:
        return g
    head, rest = g.iloc[:n], g.iloc[n:][value_col].sum()
    other = pd.DataFrame({cat_col: ["其他"], value_col: [rest]})
    return pd.concat([head, other], ignore_index=True)
