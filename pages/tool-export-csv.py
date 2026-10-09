import streamlit as st
import pandas as pd

st.title("export to CSV")


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

    csv = st.session_state.df.to_csv(index=False)
    st.download_button("Скачать CSV", csv, file_name="result.csv")
            