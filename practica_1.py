import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import requests
import pandas as pd

# def get_data_links(url):
#     """Собираем все файлы данных со страницы."""
#     response = requests.get(url, verify=False)
#     response.raise_for_status()
#     soup = BeautifulSoup(response.text, "lxml")
#
#     links = []
#     for a in soup.find_all("a", href=True):
#         href = a["href"]
#         # Нас интересуют файлы данных
#         if href.lower().endswith((".xlsx", ".xls", ".csv", ".pdf")):
#             full_url = urljoin(url, href)
#             links.append(full_url)
#     return links
#
# links1 = get_data_links("https://77.rosstat.gov.ru/folder/64640")
#
# cpi_link = None
# for link in links1:
#     if "Динамика индекса потребительских цен" in link:
#         cpi_link = link
#         break
#
# print("Нужный файл:", cpi_link)
#
# def download_file(url, filename):
#     r = requests.get(url, verify=False)
#     r.raise_for_status()
#     with open(filename, "wb") as f:
#         f.write(r.content)
#
# download_file(cpi_link, "cpi.xlsx")
# print("Файл скачан")

df = pd.read_excel("cpi.xlsx", skiprows=3, header=None)

# --- Задаём названия столбцов ---
years = df.iloc[0].tolist()
years[0] = "Месяц"  # первый столбец — Месяц
years[1:] = [int(y) for y in years[1:]]  # остальные годы как int
df.columns = years

df = df.iloc[1:].reset_index(drop=True)

df = df.iloc[:13].reset_index(drop=True)

# --- Преобразуем числовые значения в float, пустые значения станут NaN ---
for col in df.columns[1:]:
    df[col] = pd.to_numeric(
        df[col].astype(str).str.replace(",", ".", regex=False)  # запятая → точка
                  .str.replace(r"[^\d\.]", "", regex=True),      # удаляем лишние символы
        errors="coerce"
    )

df = df.drop(12).reset_index(drop=True)

df.at[df.index[-1], "Месяц"] = "Ежегодная инфляция"

annual = df[df["Месяц"] == "Ежегодная инфляция"].set_index("Месяц").T
annual = annual.rename(columns={"Ежегодная инфляция":"Инфляция"})

annual["Инфляция"] = annual["Инфляция"].astype(float)

df_long = df.melt(
    id_vars="Месяц",
    var_name="year",
    value_name="inflation_value"
)

df_long = df_long.dropna()

df_long["year"] = df_long["year"].astype(int)
df_long["inflation_value"] = df_long["inflation_value"].astype(float)

df_long.columns = ["month", "year", "inflation_value"]

from sqlalchemy import create_engine

engine = create_engine(
    "postgresql+psycopg2://postgres:root@localhost:5432/mos_stats"
)

df_long.to_sql("monthly_inflation", engine, if_exists="append", index=False)