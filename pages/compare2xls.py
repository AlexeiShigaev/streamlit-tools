import streamlit as st
import pandas as pd
import logging
from io import BytesIO
from pathlib import Path


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def normalize(s) -> str:
    """Нормализация ТОЛЬКО для сравнения (регистр, пробелы, неразрывные пробелы)."""
    if s is None or (isinstance(s, float) and pd.isna(s)):
        return ""
    return " ".join(str(s).replace("\xa0", " ").split()).lower()


st.title("🔗 Сопоставление двух Excel-таблиц")

st.markdown("""
**Что делает:** находит почту для каждого сотрудника из первого файла,
используя второй файл как справочник.

**Порядок работы:**
1. Загрузите первый файл — список сотрудников подразделения (ФИО, должность, телефон).
2. Загрузите второй файл — справочник почт всей организации (ФИО, почта).
3. Нажмите «▶️ Обработать».
4. Скачайте результат — Excel с четырьмя столбцами: ФИО, почта, должность, телефон.

⚠️ Если во втором файле есть однофамильцы (одинаковое ФИО) — берётся **первое** вхождение. Проверяйте такие строки вручную. Ненайденная почта отмечена `-`.
""")

with st.expander("📖 Подробная инструкция"):
    st.markdown(Path("pages/compare2xls.md").read_text(encoding="utf-8"))

# --- Загрузка файлов ---
file1 = st.file_uploader("Укажите файл списка сотрудников подразделения", type=["xlsx", "xls"], key="cmp_file1")
file2 = st.file_uploader("Укажите файл справочник почт",       type=["xlsx", "xls"], key="cmp_file2")

# --- Основная логика ---
if file1 and file2:
    if st.button("▶️ Обработать", type="primary"):
        st.caption("Журнал обработки")
        log = st.container(height=200, border=True, autoscroll=True)
        try:
            df1 = pd.read_excel(file1, header=None, dtype=str).fillna("")
            log.write("Загрузили первый файл")
            df2 = pd.read_excel(file2, header=None, dtype=str).fillna("")
            log.write("Загрузили второй файл")

            # --- Проверки структуры ---
            if df1.shape[1] < 6:
                msg = (
                    f"В первом файле {df1.shape[1]} столбцов, нужно минимум 6: "
                    f"склейка — по столбцам 2–4, в отчёт берутся 5-й и 6-й."
                )
                log.write("❌ " + msg)
                st.error(msg)
                st.stop()

            if df2.shape[1] < 3:
                msg = (
                    f"Во втором файле {df2.shape[1]} столбцов, нужно минимум 3: "
                    f"поиск — по 2-му, значение берётся из 3-го."
                )
                log.write("❌ " + msg)
                st.error(msg)
                st.stop()

            # --- Словарь: ключ = нормализованный 2-й столбец, значение = 3-й столбец ---
            log.write("Собираем словарь ФИО-почта из второго файла (могут быть однофамильцы).")
            lookup: dict[str, object] = {}
            for _, r in df2.iterrows():
                k = normalize(r.iloc[1])
                if not k:
                    log.write(f"Пустое ФИО в строке — пропускаю.")
                    continue
                if k in lookup:
                    log.write(
                        f"Дубликат ФИО '{r.iloc[1]}' — оставлено первое вхождение, "
                        f"последующие проверьте вручную."
                    )
                else:
                    lookup[k] = r.iloc[2]

            # --- Сборка результата ---
            keys, found = [], []
            for _, row in df1.iterrows():
                key = " ".join(str(row.iloc[i]) for i in (1, 2, 3))
                key_norm = normalize(key)
                keys.append(key)
                found.append(lookup.get(key_norm, "-"))

            log.write("Готовим выгрузку")
            result = pd.DataFrame({
                "ФИО":          keys,
                "почта":        found,
                "должность":    df1.iloc[:, 4].values,
                "телефон":      df1.iloc[:, 5].values,
            })

            # --- Вывод ---
            found_count = sum(v != "-" for v in found)
            st.dataframe(result, use_container_width=True)
            st.success(f"Готово! Обработано {len(result)} строк, найдено {found_count}.")

            # --- Скачивание ---
            output = BytesIO()
            with pd.ExcelWriter(output, engine="openpyxl") as writer:
                result.to_excel(writer, index=False, header=True)
            output.seek(0)

            st.download_button(
                label="⬇️ Скачать результат (.xlsx)",
                data=output,
                file_name="result.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
        except Exception as e:
            logger.exception("Ошибка обработки")
            st.error(f"Ошибка: {e}")
