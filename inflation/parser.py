# inflation/parser.py

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import pandas as pd
from .models import MonthlyInflation
import os
import re
from django.conf import settings


class RosStatParser:
    """Парсер для сбора данных с сайта Росстата"""

    def __init__(self):
        self.base_url = "https://77.rosstat.gov.ru/folder/64640"
        self.data_dir = os.path.join(settings.MEDIA_ROOT, 'inflation_data')
        os.makedirs(self.data_dir, exist_ok=True)

    def get_data_links(self, url):
        """Собираем все файлы данных со страницы."""
        response = requests.get(url, verify=False)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "lxml")

        links = []
        for a in soup.find_all("a", href=True):
            href = a["href"]
            if href.lower().endswith((".xlsx", ".xls")):
                full_url = urljoin(url, href)
                # Пробуем получить текст из атрибута title или из самого href
                text = a.get('title', '') or href.split('/')[-1].replace('.xlsx', '').replace('.xls', '')
                links.append((full_url, text))
        return links

    def download_file(self, url, filename):
        """Скачивает файл по URL"""
        r = requests.get(url, verify=False)
        r.raise_for_status()
        filepath = os.path.join(self.data_dir, filename)
        with open(filepath, "wb") as f:
            f.write(r.content)
        return filepath

    def parse_inflation_data(self):
        """Основной метод парсинга данных об инфляции"""
        try:
            # Получаем ссылки на файлы
            links = self.get_data_links(self.base_url)
            print(f"Найдено ссылок: {len(links)}")  # Отладка

            # Выводим первые 5 ссылок для проверки
            for i, (link, text) in enumerate(links[:5]):
                print(f"{i + 1}. Текст: '{text}'")
                print(f"   Ссылка: {link}")

            # Ищем нужный файл
            cpi_link = None
            for link, text in links:
                if "Динамика индекса потребительских цен" in text:
                    cpi_link = link
                    print(f"Найден файл: {text}")
                    break

            if not cpi_link:
                print("Файл не найден! Тексты ссылок:")
                for link, text in links:
                    print(f"'{text}'")
                return {"success": False, "message": "Файл с инфляцией не найден"}

            # Скачиваем файл
            filepath = self.download_file(cpi_link, "cpi.xlsx")
            print(f"Файл скачан: {filepath}")

            # Обрабатываем данные
            df = pd.read_excel(filepath, skiprows=3, header=None)
            print(f"Файл прочитан, форма: {df.shape}")

            # Формируем данные для БД
            months = ['Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь',
                      'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь', 'Годовая']

            data_to_save = []
            for i in range(1, 13):  # 12 месяцев
                month_num = i
                for col_idx in range(1, len(df.columns)):
                    year = df.iloc[0, col_idx]
                    if pd.notna(year):
                        try:
                            year = int(float(year))
                            value = df.iloc[i, col_idx]
                            if pd.notna(value):
                                # Преобразуем строку с запятой в число
                                if isinstance(value, str):
                                    value = float(value.replace(',', '.'))
                                data_to_save.append({
                                    'month': month_num,
                                    'year': year,
                                    'value': float(value)
                                })
                        except Exception as e:
                            print(f"Ошибка обработки: {e}")
                            continue

            print(f"Подготовлено записей: {len(data_to_save)}")

            # Очищаем старые данные и сохраняем новые
            MonthlyInflation.objects.all().delete()
            for item in data_to_save:
                MonthlyInflation.objects.create(
                    month=item['month'],
                    year=item['year'],
                    inflation_value=item['value']
                )

            return {"success": True, "message": f"Сохранено {len(data_to_save)} записей"}

        except Exception as e:
            print(f"ОШИБКА: {str(e)}")
            import traceback
            traceback.print_exc()
            return {"success": False, "message": str(e)}


# inflation/parser.py

class IncomeExpensesParser:
    """Парсер для сбора данных о доходах и расходах"""

    def __init__(self):
        self.base_url = "https://77.rosstat.gov.ru/folder/64641"
        self.data_dir = os.path.join(settings.MEDIA_ROOT, 'income_data')
        os.makedirs(self.data_dir, exist_ok=True)

    def get_data_links(self, url):
        """Собираем все файлы данных со страницы."""
        response = requests.get(url, verify=False)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "lxml")

        links = []
        for a in soup.find_all("a", href=True):
            href = a["href"]
            if href.lower().endswith((".xlsx", ".xls")):
                full_url = urljoin(url, href)
                text = a.get('title', '') or href.split('/')[-1]
                links.append((full_url, text))
        return links

    def download_file(self, url, filename):
        """Скачивает файл по URL"""
        r = requests.get(url, verify=False)
        r.raise_for_status()
        filepath = os.path.join(self.data_dir, filename)
        with open(filepath, "wb") as f:
            f.write(r.content)
        return filepath

    def parse_data(self):
        """Основной метод парсинга"""
        try:
            # Получаем ссылки
            links = self.get_data_links(self.base_url)

            # Ищем нужный файл
            target_link = None
            for link, text in links:
                if "Динамика денежных доходов населения г. Москвы" in link:
                    target_link = link
                    break

            if not target_link:
                return {"success": False, "message": "Файл не найден"}

            # Скачиваем
            filepath = self.download_file(target_link, "income.xlsx")

            # Обрабатываем
            df = pd.read_excel(filepath, header=2)
            df.rename(columns={df.columns[0]: "indicator"}, inplace=True)

            # Обработка годов
            clean_cols = ["indicator"]
            for col in df.columns[1:]:
                year = re.search(r"\d{4}", str(col))
                if year:
                    clean_cols.append(int(year.group()))

            df.columns = clean_cols

            # Обработка значений
            for col in df.columns[1:]:
                df[col] = (df[col].astype(str)
                           .str.replace(" ", "", regex=False)
                           .str.replace(",", ".", regex=False))
                df[col] = pd.to_numeric(df[col], errors="coerce")

            # Берем первые 8 строк
            df = df.iloc[:8].reset_index(drop=True)

            # Очищаем названия показателей
            df["indicator"] = (df["indicator"].astype(str)
                               .str.replace(r"\s+", " ", regex=True)
                               .str.replace('"', '', regex=False)
                               .str.strip())

            # Преобразуем в длинный формат
            df_long = pd.melt(df, id_vars=["indicator"], var_name="year", value_name="value")
            df_long = df_long.dropna()

            # Сохраняем в БД
            from .models import IncomeExpenses
            IncomeExpenses.objects.all().delete()

            for _, row in df_long.iterrows():
                IncomeExpenses.objects.create(
                    indicator=row['indicator'],
                    year=int(row['year']),
                    value=float(row['value'])
                )

            return {"success": True, "message": f"Сохранено {len(df_long)} записей"}

        except Exception as e:
            return {"success": False, "message": str(e)}


# inflation/parser.py

class IncomeShareParser:
    """Парсер для сбора данных о доле населения с денежными доходами"""

    def __init__(self):
        self.base_url = "https://77.rosstat.gov.ru/folder/64641"
        self.data_dir = os.path.join(settings.MEDIA_ROOT, 'income_share_data')
        os.makedirs(self.data_dir, exist_ok=True)

    def get_data_links(self, url):
        """Собираем все файлы данных со страницы."""
        response = requests.get(url, verify=False)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "lxml")

        links = []
        for a in soup.find_all("a", href=True):
            href = a["href"]
            if href.lower().endswith((".xlsx", ".xls")):
                full_url = urljoin(url, href)
                text = a.get('title', '') or href.split('/')[-1]
                links.append((full_url, text))
        return links

    def download_file(self, url, filename):
        """Скачивает файл по URL"""
        r = requests.get(url, verify=False)
        r.raise_for_status()
        filepath = os.path.join(self.data_dir, filename)
        with open(filepath, "wb") as f:
            f.write(r.content)
        return filepath

    def parse_data(self):
        """Основной метод парсинга"""
        try:
            # Получаем ссылки
            links = self.get_data_links(self.base_url)

            # Ищем нужный файл
            target_link = None
            for link, text in links:
                if "Доля населения с денежными доходами" in link:
                    target_link = link
                    break

            if not target_link:
                return {"success": False, "message": "Файл не найден"}

            # Скачиваем
            filepath = self.download_file(target_link, "income_share.xlsx")
            print(f"Файл скачан: {filepath}")

            # Обрабатываем
            df = pd.read_excel(filepath, skiprows=2)

            # Переименовываем столбец
            df.rename(columns={
                "В процентах от общей численности населения г. Москвы": "value"
            }, inplace=True)

            # Берем первые 14 строк
            df = df.iloc[:14].reset_index(drop=True)

            # Подготавливаем данные для БД
            data_to_save = []
            for _, row in df.iterrows():
                # Пытаемся извлечь год из первого столбца
                year_val = row.iloc[0]
                value_val = row['value']

                if pd.notna(year_val) and pd.notna(value_val):
                    try:
                        # Пробуем преобразовать год в число
                        if isinstance(year_val, (int, float)):
                            year = int(year_val)
                        else:
                            # Ищем год в строке
                            year_match = re.search(r'\d{4}', str(year_val))
                            if year_match:
                                year = int(year_match.group())
                            else:
                                continue

                        # Преобразуем значение
                        if isinstance(value_val, str):
                            value = float(value_val.replace(',', '.'))
                        else:
                            value = float(value_val)

                        data_to_save.append({
                            'year': year,
                            'value': value
                        })
                    except Exception as e:
                        print(f"Ошибка обработки строки: {e}")
                        continue

            # Сохраняем в БД
            from .models import IncomeShare
            IncomeShare.objects.all().delete()

            for item in data_to_save:
                IncomeShare.objects.create(
                    year=item['year'],
                    value=item['value']
                )

            return {"success": True, "message": f"Сохранено {len(data_to_save)} записей"}

        except Exception as e:
            print(f"ОШИБКА: {str(e)}")
            import traceback
            traceback.print_exc()
            return {"success": False, "message": str(e)}


# inflation/parser.py

class DiseaseParser:
    """Парсер для сбора данных о заболеваемости"""

    def __init__(self):
        self.base_url = "https://77.rosstat.gov.ru/folder/64643"
        self.data_dir = os.path.join(settings.MEDIA_ROOT, 'disease_data')
        os.makedirs(self.data_dir, exist_ok=True)

    def get_data_links(self, url):
        """Собираем все файлы данных со страницы."""
        response = requests.get(url, verify=False)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "lxml")

        links = []
        for a in soup.find_all("a", href=True):
            href = a["href"]
            if href.lower().endswith((".xlsx", ".xls")):
                full_url = urljoin(url, href)
                text = a.get('title', '') or href.split('/')[-1]
                links.append((full_url, text))
        return links

    def download_file(self, url, filename):
        """Скачивает файл по URL"""
        r = requests.get(url, verify=False)
        r.raise_for_status()
        filepath = os.path.join(self.data_dir, filename)
        with open(filepath, "wb") as f:
            f.write(r.content)
        return filepath

    def fix_table(self, df):
        """Вспомогательная функция для обработки таблицы"""
        first_row = pd.DataFrame([df.columns], columns=df.columns)
        df = pd.concat([first_row, df], ignore_index=True)
        df.columns = ["Показатели", 2020, 2021, 2022, 2023, 2024]
        return df

    def safe_convert(self, val):
        """Безопасное преобразование значения в float"""
        if pd.isna(val):
            return None
        if isinstance(val, str):
            val = val.replace(',', '.').strip()
            if val == 'x' or val == '' or val.lower() == 'nan':
                return None
        try:
            return float(val)
        except (ValueError, TypeError):
            return None

    def parse_data(self):
        """Основной метод парсинга"""
        try:
            # Получаем ссылки
            links = self.get_data_links(self.base_url)

            # Ищем нужный файл
            target_link = None
            for link, text in links:
                if "Заболеваемость населения по основным" in link:
                    target_link = link
                    break

            if not target_link:
                return {"success": False, "message": "Файл не найден"}

            # Скачиваем
            filepath = self.download_file(target_link, "disease.xlsx")
            print(f"Файл скачан: {filepath}")

            # Читаем файл
            df = pd.read_excel(filepath)

            # Разделяем на две таблицы
            split_index = 23  # 24-я строка

            df_abs = df.iloc[:split_index - 1].copy()
            df_1000 = df.iloc[split_index:].copy()

            # Обрабатываем первую таблицу (абсолютные значения)
            df_abs = df_abs.iloc[4:].reset_index(drop=True)
            df_abs.columns = df_abs.iloc[0]
            df_abs = df_abs.iloc[2:].reset_index(drop=True)
            df_abs = self.fix_table(df_abs)

            # Обрабатываем вторую таблицу (на 1000 человек)
            df_1000.columns = df_1000.iloc[0]
            df_1000 = df_1000.iloc[2:].reset_index(drop=True)
            df_1000.columns.name = None
            df_1000 = df_1000.iloc[:16].reset_index(drop=True)
            df_1000 = self.fix_table(df_1000)

            # Преобразуем в длинный формат и сохраняем
            from .models import DiseaseIncidence

            # Удаляем старые данные
            DiseaseIncidence.objects.all().delete()

            # Сохраняем абсолютные значения
            df_abs_long = pd.melt(df_abs, id_vars=["Показатели"], var_name="year", value_name="value")

            abs_count = 0
            for _, row in df_abs_long.iterrows():
                value = self.safe_convert(row['value'])
                if value is not None:
                    DiseaseIncidence.objects.create(
                        table_type='absolute',
                        indicator=row['Показатели'],
                        year=int(row['year']),
                        value=value
                    )
                    abs_count += 1

            # Сохраняем значения на 1000 человек
            df_1000_long = pd.melt(df_1000, id_vars=["Показатели"], var_name="year", value_name="value")

            per1000_count = 0
            for _, row in df_1000_long.iterrows():
                value = self.safe_convert(row['value'])
                if value is not None:
                    DiseaseIncidence.objects.create(
                        table_type='per_1000',
                        indicator=row['Показатели'],
                        year=int(row['year']),
                        value=value
                    )
                    per1000_count += 1

            total = abs_count + per1000_count
            return {"success": True,
                    "message": f"Сохранено {total} записей (абс: {abs_count}, на 1000: {per1000_count})"}

        except Exception as e:
            print(f"ОШИБКА: {str(e)}")
            import traceback
            traceback.print_exc()
            return {"success": False, "message": str(e)}


# inflation/parser.py

class MedicalPersonnelParser:
    """Парсер для сбора данных о медицинских кадрах"""

    def __init__(self):
        self.base_url = "https://77.rosstat.gov.ru/folder/64643"
        self.data_dir = os.path.join(settings.MEDIA_ROOT, 'medical_data')
        os.makedirs(self.data_dir, exist_ok=True)

    def get_data_links(self, url):
        """Собираем все файлы данных со страницы."""
        response = requests.get(url, verify=False)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "lxml")

        links = []
        for a in soup.find_all("a", href=True):
            href = a["href"]
            if href.lower().endswith((".xlsx", ".xls")):
                full_url = urljoin(url, href)
                text = a.get('title', '') or href.split('/')[-1]
                links.append((full_url, text))
        return links

    def download_file(self, url, filename):
        """Скачивает файл по URL"""
        r = requests.get(url, verify=False)
        r.raise_for_status()
        filepath = os.path.join(self.data_dir, filename)
        with open(filepath, "wb") as f:
            f.write(r.content)
        return filepath

    def safe_convert(self, val):
        """Безопасное преобразование значения в float"""
        if pd.isna(val):
            return None
        if isinstance(val, str):
            val = val.replace(',', '.').strip()
            if val == '' or val.lower() == 'nan' or val == '-':
                return None
        try:
            return float(val)
        except (ValueError, TypeError):
            return None

    def parse_data(self):
        """Основной метод парсинга"""
        try:
            # Получаем ссылки
            links = self.get_data_links(self.base_url)

            # Ищем нужный файл
            target_link = None
            for link, text in links:
                if "Численность медицинских кадров" in link:
                    target_link = link
                    break

            if not target_link:
                return {"success": False, "message": "Файл не найден"}

            # Скачиваем
            filepath = self.download_file(target_link, "medical.xlsx")
            print(f"Файл скачан: {filepath}")

            # Читаем файл
            df = pd.read_excel(filepath, skiprows=2)

            # Переименовываем столбцы
            df.columns = [
                "Годы",
                "Врачи_всего",
                "Врачи_на_10000",
                "Персонал_всего",
                "Персонал_на_10000"
            ]

            # Удаляем первую строку (заголовки)
            df = df.iloc[1:].reset_index(drop=True)

            # Создаем две отдельные таблицы
            df_doctors = df[["Годы", "Врачи_всего", "Врачи_на_10000"]].copy()
            df_staff = df[["Годы", "Персонал_всего", "Персонал_на_10000"]].copy()

            # Удаляем последние две строки (итоги)
            df_doctors = df_doctors.iloc[:-2].reset_index(drop=True)
            df_staff = df_staff.iloc[:-2].reset_index(drop=True)

            # Сохраняем в БД
            from .models import MedicalPersonnel
            MedicalPersonnel.objects.all().delete()

            doctors_total_count = 0
            doctors_per10000_count = 0
            staff_total_count = 0
            staff_per10000_count = 0

            # Обрабатываем данные по врачам
            for _, row in df_doctors.iterrows():
                year = self.safe_convert(row["Годы"])
                if year is None:
                    continue
                year = int(year)

                # Врачи всего
                value = self.safe_convert(row["Врачи_всего"])
                if value is not None:
                    MedicalPersonnel.objects.create(
                        personnel_type='doctors',
                        value_type='total',
                        year=year,
                        value=value
                    )
                    doctors_total_count += 1

                # Врачи на 10000
                value = self.safe_convert(row["Врачи_на_10000"])
                if value is not None:
                    MedicalPersonnel.objects.create(
                        personnel_type='doctors',
                        value_type='per_10000',
                        year=year,
                        value=value
                    )
                    doctors_per10000_count += 1

            # Обрабатываем данные по среднему медперсоналу
            for _, row in df_staff.iterrows():
                year = self.safe_convert(row["Годы"])
                if year is None:
                    continue
                year = int(year)

                # Персонал всего
                value = self.safe_convert(row["Персонал_всего"])
                if value is not None:
                    MedicalPersonnel.objects.create(
                        personnel_type='nursing',
                        value_type='total',
                        year=year,
                        value=value
                    )
                    staff_total_count += 1

                # Персонал на 10000
                value = self.safe_convert(row["Персонал_на_10000"])
                if value is not None:
                    MedicalPersonnel.objects.create(
                        personnel_type='nursing',
                        value_type='per_10000',
                        year=year,
                        value=value
                    )
                    staff_per10000_count += 1

            total = doctors_total_count + doctors_per10000_count + staff_total_count + staff_per10000_count
            return {
                "success": True,
                "message": f"Сохранено {total} записей (врачи: абс={doctors_total_count}, на 10000={doctors_per10000_count}; персонал: абс={staff_total_count}, на 10000={staff_per10000_count})"
            }

        except Exception as e:
            print(f"ОШИБКА: {str(e)}")
            import traceback
            traceback.print_exc()
            return {"success": False, "message": str(e)}