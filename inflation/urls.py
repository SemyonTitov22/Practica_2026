# inflation/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('api/data/', views.get_data, name='api_data'),  # переименовал
    path('api/years/', views.get_years, name='api_years'),
    path('api/update/', views.update_data, name='api_update'),
    path('income-share/', views.income_share_page, name='income_share'),
    path('inflation/', views.inflation_page, name='inflation'),
    path('disease/', views.disease_page, name='disease'),
    path('medical/', views.medical_page, name='medical'),


    # Новые маршруты для доходов
    path('api/income/data/', views.get_income_data, name='api_income_data'),
    path('api/income/years/', views.get_income_years, name='api_income_years'),
    path('api/income/update/', views.update_income_data, name='api_income_update'),
    path('income/', views.income_page, name='income_page'),


    path('api/income-share/data/', views.get_income_share_data, name='api_income_share_data'),
    path('api/income-share/years/', views.get_income_share_years, name='api_income_share_years'),
    path('api/income-share/update/', views.update_income_share_data, name='api_income_share_update'),


    path('api/disease/data/', views.get_disease_data, name='api_disease_data'),
    path('api/disease/years/', views.get_disease_years, name='api_disease_years'),
    path('api/disease/update/', views.update_disease_data, name='api_disease_update'),


    path('api/medical/data/', views.get_medical_data, name='api_medical_data'),
    path('api/medical/years/', views.get_medical_years, name='api_medical_years'),
    path('api/medical/update/', views.update_medical_data, name='api_medical_update'),


]