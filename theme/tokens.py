"""主题 token：全站唯一的颜色与字体来源（契约见 .ths/PROJECT.md）。"""

# 分类色序（顺序即 CVD 安全机制，不得循环取色；超 8 个系列并入「其他」）
SERIES = [
    "#2a78d6",  # 蓝
    "#eb6834",  # 橙
    "#1baf7a",  # 青绿
    "#eda100",  # 黄
    "#e87ba4",  # 品红
    "#008300",  # 绿
    "#4a3aa7",  # 紫
    "#e34948",  # 红
]

# 序列渐变（单一蓝色相，浅→深；热力图/漏斗等量级编码用）
SEQ_BLUE = [
    "#cde2fb", "#b7d3f6", "#9ec5f4", "#86b6ef", "#6da7ec",
    "#5598e7", "#3987e5", "#2a78d6", "#256abf", "#1c5cab",
    "#184f95", "#104281", "#0d366b",
]

PAGE = "#f9f9f7"        # 页面底
SURFACE = "#fcfcfb"     # 卡面/图面
INK = "#0b0b0b"         # 正文墨
INK_2 = "#52514e"       # 次级墨
MUTED = "#898781"       # 弱化（轴标签）
GRID = "#e1e0d9"        # 发丝网格
BASELINE = "#c3c2b7"    # 轴基线
BORDER = "rgba(11,11,11,0.10)"  # 发丝描边

GOOD = "#006300"        # 向好增量文字色
BAD = "#d03b3b"         # 向坏增量文字色

FONT = 'system-ui, -apple-system, "Segoe UI", "PingFang SC", "Microsoft YaHei", sans-serif'
