# inflation/views.py

from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import MonthlyInflation, IncomeExpenses, IncomeShare, DiseaseIncidence, MedicalPersonnel
from .parser import RosStatParser, IncomeExpensesParser, IncomeShareParser, DiseaseParser, MedicalPersonnelParser


def index(request):
    """Главная страница"""
    return render(request, 'inflation/index.html')

def inflation_page(request):
    """Страница с инфляцией"""
    return render(request, 'inflation/inflation.html')


def get_data(request):
    """Получение данных из БД"""
    year = request.GET.get('year')
    month = request.GET.get('month')

    queryset = MonthlyInflation.objects.all()

    if year:
        queryset = queryset.filter(year=year)
    if month and month.isdigit():
        queryset = queryset.filter(month=int(month))

    data = []
    for item in queryset:
        month_name = dict(MonthlyInflation.MONTH_CHOICES).get(item.month, str(item.month))
        data.append({
            'month': month_name,
            'year': item.year,
            'inflation_value': item.inflation_value,
        })

    return JsonResponse({'data': data})


def get_years(request):
    """Получение списка доступных годов"""
    years = MonthlyInflation.objects.values_list('year', flat=True).distinct().order_by('-year')
    return JsonResponse({'years': list(years)})


@csrf_exempt
def update_data(request):
    """Обновление данных через парсер"""
    if request.method == 'POST':
        parser = RosStatParser()
        result = parser.parse_inflation_data()
        return JsonResponse(result)
    return JsonResponse({'success': False, 'message': 'Метод не поддерживается'})


@csrf_exempt
def update_income_data(request):
    """Обновление данных о доходах"""
    if request.method == 'POST':
        parser = IncomeExpensesParser()
        result = parser.parse_data()
        return JsonResponse(result)
    return JsonResponse({'success': False, 'message': 'Метод не поддерживается'})


def get_income_data(request):
    """Получение данных о доходах из БД"""
    year = request.GET.get('year')

    queryset = IncomeExpenses.objects.all()
    if year:
        queryset = queryset.filter(year=year)

    data = []
    for item in queryset:
        data.append({
            'indicator': item.indicator,
            'year': item.year,
            'value': item.value,
        })

    return JsonResponse({'data': data})


def get_income_years(request):
    """Получение списка годов для доходов"""
    years = IncomeExpenses.objects.values_list('year', flat=True).distinct().order_by('-year')
    return JsonResponse({'years': list(years)})

def income_page(request):
    """Страница с доходами"""
    return render(request, 'inflation/income.html')





@csrf_exempt
def update_income_share_data(request):
    """Обновление данных о доле населения"""
    if request.method == 'POST':
        parser = IncomeShareParser()
        result = parser.parse_data()
        return JsonResponse(result)
    return JsonResponse({'success': False, 'message': 'Метод не поддерживается'})

def get_income_share_data(request):
    """Получение данных о доле населения из БД"""
    year = request.GET.get('year')

    queryset = IncomeShare.objects.all()
    if year:
        queryset = queryset.filter(year=year)

    data = []
    for item in queryset:
        data.append({
            'year': item.year,
            'value': item.value,
        })

    return JsonResponse({'data': data})

def get_income_share_years(request):
    """Получение списка годов"""
    years = IncomeShare.objects.values_list('year', flat=True).distinct().order_by('-year')
    return JsonResponse({'years': list(years)})

def income_share_page(request):
    """Страница с долей населения"""
    return render(request, 'inflation/income_share.html')




@csrf_exempt
def update_disease_data(request):
    """Обновление данных о заболеваемости"""
    if request.method == 'POST':
        parser = DiseaseParser()
        result = parser.parse_data()
        return JsonResponse(result)
    return JsonResponse({'success': False, 'message': 'Метод не поддерживается'})

def get_disease_data(request):
    """Получение данных о заболеваемости из БД"""
    year = request.GET.get('year')
    table_type = request.GET.get('table_type', 'absolute')  # по умолчанию absolute

    queryset = DiseaseIncidence.objects.filter(table_type=table_type)
    if year:
        queryset = queryset.filter(year=year)

    data = []
    for item in queryset:
        data.append({
            'indicator': item.indicator,
            'year': item.year,
            'value': item.value,
        })

    return JsonResponse({'data': data})

def get_disease_years(request):
    """Получение списка годов"""
    years = DiseaseIncidence.objects.values_list('year', flat=True).distinct().order_by('-year')
    return JsonResponse({'years': list(years)})

def disease_page(request):
    """Страница с заболеваемостью"""
    return render(request, 'inflation/disease.html')



@csrf_exempt
def update_medical_data(request):
    """Обновление данных о медицинских кадрах"""
    if request.method == 'POST':
        parser = MedicalPersonnelParser()
        result = parser.parse_data()
        return JsonResponse(result)
    return JsonResponse({'success': False, 'message': 'Метод не поддерживается'})

def get_medical_data(request):
    """Получение данных о медицинских кадрах из БД"""
    year = request.GET.get('year')
    personnel_type = request.GET.get('personnel_type', 'doctors')
    value_type = request.GET.get('value_type', 'total')

    queryset = MedicalPersonnel.objects.filter(
        personnel_type=personnel_type,
        value_type=value_type
    )
    if year:
        queryset = queryset.filter(year=year)

    data = []
    for item in queryset:
        data.append({
            'year': item.year,
            'value': item.value,
        })

    return JsonResponse({'data': data})

def get_medical_years(request):
    """Получение списка годов"""
    years = MedicalPersonnel.objects.values_list('year', flat=True).distinct().order_by('-year')
    return JsonResponse({'years': list(years)})

def medical_page(request):
    """Страница с медицинскими кадрами"""
    return render(request, 'inflation/medical.html')