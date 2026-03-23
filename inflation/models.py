# inflation/models.py

from django.db import models


class MonthlyInflation(models.Model):
    """Модель для хранения данных об инфляции"""
    MONTH_CHOICES = [
        (1, 'Январь'),
        (2, 'Февраль'),
        (3, 'Март'),
        (4, 'Апрель'),
        (5, 'Май'),
        (6, 'Июнь'),
        (7, 'Июль'),
        (8, 'Август'),
        (9, 'Сентябрь'),
        (10, 'Октябрь'),
        (11, 'Ноябрь'),
        (12, 'Декабрь'),
        (13, 'Ежегодная инфляция'),
    ]

    month = models.IntegerField(choices=MONTH_CHOICES, verbose_name="Месяц")
    year = models.IntegerField(verbose_name="Год")
    inflation_value = models.FloatField(verbose_name="Значение инфляции")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Инфляция"
        verbose_name_plural = "Инфляция по месяцам"
        ordering = ['year', 'month']
        unique_together = ['month', 'year']  # Чтобы не было дубликатов

    def __str__(self):
        month_name = dict(self.MONTH_CHOICES).get(self.month, str(self.month))
        return f"{month_name} {self.year}: {self.inflation_value}%"


# inflation/models.py

class IncomeExpenses(models.Model):
    """Модель для хранения данных о доходах и расходах"""
    INDICATOR_CHOICES = [
        ('Денежные доходы', 'Денежные доходы'),
        ('Оплата труда', 'Оплата труда'),
        ('Социальные выплаты', 'Социальные выплаты'),
        ('Доходы от предпринимательства', 'Доходы от предпринимательства'),
        ('Доходы от собственности', 'Доходы от собственности'),
        ('Другие доходы', 'Другие доходы'),
        ('Потребительские расходы', 'Потребительские расходы'),
        ('Обязательные платежи', 'Обязательные платежи'),
    ]

    indicator = models.CharField(max_length=100, choices=INDICATOR_CHOICES, verbose_name="Показатель")
    year = models.IntegerField(verbose_name="Год")
    value = models.FloatField(verbose_name="Значение")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Доходы и расходы"
        verbose_name_plural = "Доходы и расходы"
        ordering = ['year', 'indicator']
        unique_together = ['indicator', 'year']

    def __str__(self):
        return f"{self.indicator} {self.year}: {self.value}"



class IncomeShare(models.Model):
    """Модель для хранения данных о доле населения с денежными доходами"""
    year = models.IntegerField(verbose_name="Год")
    value = models.FloatField(verbose_name="Доля в %")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Доля населения с доходами"
        verbose_name_plural = "Доля населения с денежными доходами"
        ordering = ['year']

    def __str__(self):
        return f"{self.year}: {self.value}%"


# inflation/models.py

class DiseaseIncidence(models.Model):
    """Модель для хранения данных о заболеваемости"""
    TABLE_CHOICES = [
        ('absolute', 'Абсолютные значения'),
        ('per_1000', 'На 1000 человек'),
    ]

    table_type = models.CharField(max_length=20, choices=TABLE_CHOICES, verbose_name="Тип таблицы")
    indicator = models.CharField(max_length=200, verbose_name="Показатель")
    year = models.IntegerField(verbose_name="Год")
    value = models.FloatField(verbose_name="Значение")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Заболеваемость"
        verbose_name_plural = "Заболеваемость населения"
        ordering = ['table_type', 'year', 'indicator']
        unique_together = ['table_type', 'indicator', 'year']

    def __str__(self):
        table_display = dict(self.TABLE_CHOICES).get(self.table_type, self.table_type)
        return f"{table_display} - {self.indicator} {self.year}: {self.value}"


# inflation/models.py

class MedicalPersonnel(models.Model):
    """Модель для хранения данных о медицинских кадрах"""
    PERSONNEL_TYPE_CHOICES = [
        ('doctors', 'Врачи'),
        ('nursing', 'Средний медперсонал'),
    ]
    VALUE_TYPE_CHOICES = [
        ('total', 'Абсолютное значение'),
        ('per_10000', 'На 10000 человек'),
    ]

    personnel_type = models.CharField(max_length=20, choices=PERSONNEL_TYPE_CHOICES, verbose_name="Тип персонала")
    value_type = models.CharField(max_length=20, choices=VALUE_TYPE_CHOICES, verbose_name="Тип значения")
    year = models.IntegerField(verbose_name="Год")
    value = models.FloatField(verbose_name="Значение")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Медицинские кадры"
        verbose_name_plural = "Численность медицинских кадров"
        ordering = ['personnel_type', 'year']
        unique_together = ['personnel_type', 'value_type', 'year']

    def __str__(self):
        return f"{self.get_personnel_type_display()} - {self.get_value_type_display()} {self.year}: {self.value}"