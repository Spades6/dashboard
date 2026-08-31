"""导出按钮：Excel（多 sheet）与 PDF（标题+KPI 表+要点）。"""

import io

import pandas as pd
import streamlit as st
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import ParagraphStyle

_CN_FONT = "STSong-Light"  # reportlab 内置 CID 中文字体，无需字体文件


@st.cache_data(show_spinner=False)
def excel_bytes(dfs: dict[str, pd.DataFrame]) -> bytes:
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        for sheet, df in dfs.items():
            df.to_excel(writer, sheet_name=sheet[:31], index=False)
    return buf.getvalue()


def excel_download_button(dfs: dict[str, pd.DataFrame], filename: str,
                          label: str = "⬇️ 导出 Excel") -> None:
    st.download_button(
        label, data=excel_bytes(dfs), file_name=filename,
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        key=f"xlsx_{filename}",
    )


@st.cache_data(show_spinner=False)
def pdf_bytes(title: str, kpis: list[tuple[str, str]], notes: list[str]) -> bytes:
    pdfmetrics.registerFont(UnicodeCIDFont(_CN_FONT))
    h1 = ParagraphStyle("h1", fontName=_CN_FONT, fontSize=18, leading=24)
    body = ParagraphStyle("body", fontName=_CN_FONT, fontSize=11, leading=16)

    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4,
                            leftMargin=18 * mm, rightMargin=18 * mm,
                            topMargin=18 * mm, bottomMargin=18 * mm)
    story = [Paragraph(title, h1), Spacer(1, 8 * mm)]
    if kpis:
        table = Table([[k, v] for k, v in kpis], colWidths=[70 * mm, 90 * mm])
        table.setStyle(TableStyle([
            ("FONTNAME", (0, 0), (-1, -1), _CN_FONT),
            ("FONTSIZE", (0, 0), (-1, -1), 11),
            ("TEXTCOLOR", (0, 0), (0, -1), colors.HexColor("#52514e")),
            ("LINEBELOW", (0, 0), (-1, -1), 0.5, colors.HexColor("#e1e0d9")),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ]))
        story += [table, Spacer(1, 8 * mm)]
    for note in notes:
        story.append(Paragraph(f"· {note}", body))
    doc.build(story)
    return buf.getvalue()


def pdf_download_button(title: str, kpis: list[tuple[str, str]], notes: list[str],
                        filename: str, label: str = "⬇️ 导出 PDF") -> None:
    st.download_button(
        label, data=pdf_bytes(title, kpis, notes), file_name=filename,
        mime="application/pdf", key=f"pdf_{filename}",
    )
