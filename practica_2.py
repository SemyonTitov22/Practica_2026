import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import pandas as pd
import re
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

links1 = get_data_links("https://77.rosstat.gov.ru/folder/64641")

cpi_link = None
for link in links1:
    if "Динамика денежных доходов населения г. Москвы" in link:
        cpi_link = link
        break

print("Нужный файл:", cpi_link)

import requests

def download_file(url, filename):
    r = requests.get(url, verify=False)
    r.raise_for_status()
    with open(filename, "wb") as f:
        f.write(r.content)

download_file(cpi_link, "cpi_1.xlsx")
print("Файл скачан")

df = pd.read_excel("cpi_1.xlsx", header=2)

df.rename(columns={df.columns[0]: "Показатели"}, inplace=True)

clean_cols = ["Показатели"]


for col in df.columns[1:]:
    year = re.search(r"\d{4}", str(col)).group()  # берём первые 4 цифры
    clean_cols.append(int(year))

df.columns = clean_cols

for col in df.columns[1:]:
    df[col] = (
        df[col].astype(str)
        .str.replace(" ", "", regex=False)  # убрать пробелы в числах
        .str.replace(",", ".", regex=False)
    )
    df[col] = pd.to_numeric(df[col], errors="coerce")

df = df.iloc[:8].reset_index(drop=True)

df["Показатели"] = (
    df["Показатели"]
    .astype(str)
    .str.replace(r"\s+", " ", regex=True)  # любые пробелы/переносы/табы → один пробел
    .str.replace('"', '', regex=False)
    .str.strip()
)

df["Показатели"] = df["Показатели"].str.replace("\n", " ", regex=False)

df_long = pd.melt(
    df,
    id_vars=["Показатели"],
    var_name="year",
    value_name="value"
)

# Переименовываем колонки под таблицу в БД
df_long = df_long.rename(columns={"Показатели": "indicator"})

# Подключаемся к PostgreSQL
engine = create_engine("postgresql+psycopg2://postgres:root@localhost:5432/mos_stats")

# Загружаем
df_long.to_sql("income_expenses", engine, if_exists="append", index=False)

print("Готово!")