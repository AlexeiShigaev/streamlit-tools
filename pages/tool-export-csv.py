import streamlit as st
import pandas as pd
from pathlib import Path

st.title("📄 Excel → CSV")

st.markdown("""
**Что делает:** превращает листы Excel-журнала в отдельные CSV-файлы.
На выходе — три столбца: номер, ФИО, школа.

**Порядок работы:**
1. Загрузите Excel-файл.
2. Выберите лист.
3. Отметьте лишние столбцы и нажмите «Удалить столбцы». Можно в несколько подходов.
4. Как только останется ровно **5 столбцов** — ФИО склеится автоматически, останутся три: номер, ФИО, школа.
5. Скачайте CSV и переходите к следующему листу.

⚠️ Столбцы удаляются **вручную** — утилита не знает, какие из них мусорные. Порядок обхода листов не важен.
""")

with st.expander("📖 Подробная инструкция"):
    st.markdown(Path("pages/tool-export-csv.md").read_text(encoding="utf-8"))

uploaded = st.file_uploader("Загрузите журнал сертификатов смены", type=["xlsx", "xls"])

if uploaded is not None:
    xls = pd.ExcelFile(uploaded)
    
    st.cache_data.clear()
    
    sheets = xls.sheet_names
    sheet = st.selectbox("Выбрать лист", sheets)
    
    if "df" not in st.session_state or "loaded_sheet" not in st.session_state or st.session_state.loaded_sheet != sheet:
        st.session_state.df = pd.read_excel(uploaded, sheet_name=sheet,dtype=str)
        st.session_state.loaded_sheet = sheet
    
    df = st.session_state.df
    
    st.subheader("Должно остаться 5 столбцов.\nПереносы строк в ОУ не показываются.")
    st.dataframe(df)
    
    cols_to_delete = st.multiselect(
        "Выберите столбцы для удаления",
        df.columns.tolist()
    )

    if st.button("Удалить выбранные столбцы"):
        df = df.drop(columns=cols_to_delete)

        df = df[df.iloc[:, 0].notna() & (df.iloc[:, 0].astype(str).str.strip() != "")]
        
        st.session_state.df = df
        st.rerun()


    if len(df.columns) == 5:
        name = (
            df.iloc[:, 1].astype(str) + " " +
            df.iloc[:, 2].astype(str) + " " +
            df.iloc[:, 3].astype(str)
        )
        df.insert(1, "name", name)
        
        df = df.drop(columns=[df.columns[2], df.columns[3], df.columns[4]])
        
        df.columns = ["nomer", "name", "shkola"]
        
        st.session_state.df = df
        st.rerun()

    csv = st.session_state.df.to_csv(index=False, encoding="utf-8-sig")
    st.download_button("Скачать CSV", csv, file_name="result.csv")
            