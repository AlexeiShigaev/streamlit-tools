import streamlit as st

st.set_page_config(page_title="Streamlit Tools", layout="centered")
st.title("Инструменты")

st.page_link("pages/tool-export-csv.py", label="📄 Excel → CSV", icon="🔄")
st.page_link("pages/compare2xls.py", label="🔗 Сопоставление Excel-таблиц", icon="⚙️")