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

links2 = get_data_links("https://77.rosstat.gov.ru/folder/64641")

cpi_link = None
for link in links2:
    if "Доля населения с денежными доходами" in link:
        cpi_link = link
        break

print("Нужный файл:", cpi_link)

def download_file(url, filename):
    r = requests.get(url, verify=False)
    r.raise_for_status()
    with open(filename, "wb") as f:
        f.write(r.content)

download_file(cpi_link, "cpi_2.xlsx")
print("Файл скачан")

df = pd.read_excel("cpi_2.xlsx", skiprows=2)

df.rename(columns={
    "В процентах от общей численности населения г. Москвы": "Проценты"
}, inplace=True)

df = df.iloc[:14].reset_index(drop=True)

df = df.rename(columns={'Годы': 'year', 'Проценты': 'percent'})

engine = create_engine("postgresql+psycopg2://postgres:root@localhost:5432/mos_stats")

# Загружаем
df.to_sql("interest_rates", engine, if_exists="append", index=False)

print("Готово!")

