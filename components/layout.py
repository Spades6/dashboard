"""页面统一入口：set_page_config + 全站 CSS + plotly 模板。每页首行调用 setup_page()。"""

import streamlit as st

from theme import plotly_theme, tokens

_CSS = f"""
<style>
#MainMenu, footer {{visibility: hidden;}}
.stApp {{background-color: {tokens.PAGE};}}
h1, h2, h3 {{letter-spacing: -0.01em;}}
.block-container {{padding-top: 2.5rem; max-width: 1200px;}}

.spade-metric {{
  background: {tokens.SURFACE};
  border: 1px solid {tokens.BORDER};
  border-radius: 12px;
  padding: 16px 20px;
}}
.spade-metric .m-label {{
  color: {tokens.INK_2}; font-size: 13px; margin-bottom: 4px;
}}
.spade-metric .m-value {{
  color: {tokens.INK}; font-size: 28px; font-weight: 600; line-height: 1.2;
}}
.spade-metric .m-delta {{font-size: 13px; margin-top: 4px;}}
.spade-metric .m-delta.good {{color: {tokens.GOOD};}}
.spade-metric .m-delta.bad {{color: {tokens.BAD};}}
.spade-metric .m-delta.flat {{color: {tokens.MUTED};}}
</style>
"""


def setup_page(title: str, icon: str) -> None:
    st.set_page_config(page_title=title, page_icon=icon, layout="wide")
    plotly_theme.register()
    st.markdown(_CSS, unsafe_allow_html=True)


def page_header(title: str, subtitle: str = "") -> None:
    st.title(title)
    if subtitle:
        st.caption(subtitle)
