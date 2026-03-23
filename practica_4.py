import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import pandas as pd
import requests
from sqlalchemy import create_engine

def get_data_links(url):
    """Собираем все файлы данных со страницы."""
    response = requests.get(url, verify=False)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "lxml")

    links = []
    for a in soup.find_all("a", href=True):
        href = a["href"]
        # Нас интересуют файлы данных
        if href.lower().endswith((".xlsx", ".xls", ".csv", ".pdf")):
            full_url = urljoin(url, href)
            links.append(full_url)
    return links

links3 = get_data_links("https://77.rosstat.gov.ru/folder/64643")

cpi_link = None
for link in links3:
    if "Заболеваемость населения по основным" in link:
        cpi_link = link
        break

print("Нужный файл:", cpi_link)

def download_file(url, filename):
    r = requests.get(url, verify=False)
    r.raise_for_status()
    with open(filename, "wb") as f:
        f.write(r.content)

download_file(cpi_link, "cpi_3.xlsx")
print("Файл скачан")

df = pd.read_excel("cpi_3.xlsx")

df.head()

split_index = 23  # 24-я строка в Excel

df_abs = df.iloc[:split_index-1].copy()
df_1000 = df.iloc[split_index:].copy()

df_abs = df_abs.iloc[4:].reset_index(drop=True)

df_abs.columns = df_abs.iloc[0]

# удаляем эту строку из данных
df_abs = df_abs.iloc[2:].reset_index(drop=True)

df_1000.columns = df_1000.iloc[0]

df_1000 = df_1000.iloc[2:].reset_index(drop=True)

df_1000.columns.name = None

df_1000 = df_1000.iloc[:16].reset_index(drop=True)

def fix_table(df):
    # сохраняем текущие названия столбцов как первую строку
    first_row = pd.DataFrame([df.columns], columns=df.columns)

    # добавляем её сверху
    df = pd.concat([first_row, df], ignore_index=True)

    # задаём правильные названия столбцов
    df.columns = ["Показатели", 2020, 2021, 2022, 2023, 2024]

    return df

df_abs = fix_table(df_abs)
df_1000 = fix_table(df_1000)

engine = create_engine("postgresql+psycopg2://postgres:root@localhost:5432/mos_stats")


# Функция для преобразования и загрузки
def load_disease_table(df, table_name):
    # Переводим в длинный формат
    df_long = pd.melt(
        df,
        id_vars=["Показатели"],
        var_name="year",
        value_name="value"
    )

    # Переименовываем колонку
    df_long = df_long.rename(columns={"Показатели": "disease_name"})

    # Удаляем строки с "х" (нет данных)
    df_long = df_long[df_long["value"] != "х"]

    # Преобразуем value в число
    df_long["value"] = pd.to_numeric(df_long["value"], errors="coerce")

    # Удаляем NaN
    df_long = df_long.dropna()

    # Загружаем
    df_long.to_sql(table_name, engine, if_exists="append", index=False)
    print(f"Загружено {len(df_long)} строк в {table_name}")


# Загружаем обе таблицы
load_disease_table(df_abs, "diseases_absolute")
load_disease_table(df_1000, "diseases_per_1000")

print("Готово!")

