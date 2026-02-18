import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

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

links4 = get_data_links("https://77.rosstat.gov.ru/folder/64643")

cpi_link = None
for link in links4:
    if "Численность медицинских кадров" in link:
        cpi_link = link
        break

print("Нужный файл:", cpi_link)

import requests

def download_file(url, filename):
    r = requests.get(url, verify=False)
    r.raise_for_status()
    with open(filename, "wb") as f:
        f.write(r.content)

download_file(cpi_link, "cpi_4.xlsx")
print("Файл скачан")

import pandas as pd

df = pd.read_excel("cpi_4.xlsx", skiprows=2)

df.columns = [
    "Годы",
    "Врачи_всего",
    "Врачи_на_10000",
    "Персонал_всего",
    "Персонал_на_10000"
]

df = df.iloc[1:].reset_index(drop=True)

df_doctors = df[["Годы", "Врачи_всего", "Врачи_на_10000"]]
df_staff = df[["Годы", "Персонал_всего", "Персонал_на_10000"]]

for col in ["Врачи_всего", "Врачи_на_10000"]:
    df_doctors[col] = pd.to_numeric(df_doctors[col], errors="coerce")

for col in ["Персонал_всего", "Персонал_на_10000"]:
    df_staff[col] = pd.to_numeric(df_staff[col], errors="coerce")

df_doctors = df_doctors.iloc[:-2].reset_index(drop=True)
df_staff = df_staff.iloc[:-2].reset_index(drop=True)

engine = create_engine("postgresql+psycopg2://postgres:root@localhost:5432/mos_stats")

# Переименовываем колонки под таблицы в БД
df_doctors = df_doctors.rename(columns={
    "Годы": "year",
    "Врачи_всего": "total_doctors",
    "Врачи_на_10000": "doctors_per_10000"
})

df_staff = df_staff.rename(columns={
    "Годы": "year",
    "Персонал_всего": "total_staff",
    "Персонал_на_10000": "staff_per_10000"
})

# Загружаем
df_doctors.to_sql("medical_doctors", engine, if_exists="append", index=False)
df_staff.to_sql("medical_staff", engine, if_exists="append", index=False)

print("Данные загружены!")
