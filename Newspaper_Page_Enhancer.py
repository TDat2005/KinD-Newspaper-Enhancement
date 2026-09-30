"""Standalone local Streamlit demo for restoring a photographed newspaper page."""

import streamlit as st

from newspaper_parts.ui import render_app


st.set_page_config(
    page_title="Khôi phục ảnh trang báo",
    page_icon="📰",
    layout="wide",
    initial_sidebar_state="expanded",
)

render_app()
