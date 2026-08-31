"""注册全站统一的 plotly 模板 "spade"。"""

import plotly.graph_objects as go
import plotly.io as pio

from theme import tokens


def register() -> None:
    if "spade" in pio.templates:
        pio.templates.default = "spade"
        return
    pio.templates["spade"] = go.layout.Template(
        layout=go.Layout(
            colorway=tokens.SERIES,
            paper_bgcolor=tokens.SURFACE,
            plot_bgcolor=tokens.SURFACE,
            font=dict(family=tokens.FONT, color=tokens.INK, size=13),
            title=dict(font=dict(size=15, color=tokens.INK), x=0, xanchor="left",
                       y=0.97, yanchor="top"),
            margin=dict(l=48, r=16, t=76, b=40),
            xaxis=dict(
                gridcolor=tokens.GRID, linecolor=tokens.BASELINE,
                tickcolor=tokens.BASELINE, tickfont=dict(color=tokens.MUTED),
                zeroline=False, automargin=True,
                title=dict(standoff=10, font=dict(color=tokens.MUTED, size=12)),
            ),
            yaxis=dict(
                gridcolor=tokens.GRID, linecolor=tokens.BASELINE,
                tickcolor=tokens.BASELINE, tickfont=dict(color=tokens.MUTED),
                zeroline=False, automargin=True,
                title=dict(standoff=10, font=dict(color=tokens.MUTED, size=12)),
            ),
            legend=dict(
                orientation="h", yanchor="bottom", y=1.02, x=0,
                font=dict(color=tokens.INK_2),
            ),
            hoverlabel=dict(
                bgcolor=tokens.INK, font=dict(color="#ffffff", family=tokens.FONT),
                bordercolor=tokens.INK,
            ),
        ),
        data=dict(
            scatter=[go.Scatter(line=dict(width=2), marker=dict(size=8))],
            bar=[go.Bar(marker=dict(cornerradius=4))],
        ),
    )
    pio.templates.default = "spade"
