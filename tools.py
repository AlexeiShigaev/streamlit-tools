import streamlit as st

st.set_page_config(page_title="Streamlit Tools", layout="centered")

pages = [
    st.Page(
        "pages/compare2xls.py",
        title="Сопоставление Excel",
        icon="🔗",
        default=True,
    ),
    st.Page(
        "pages/tool-export-csv.py",
        title="Excel → CSV",
        icon="📄",
    ),
]

st.navigation(pages).run()
