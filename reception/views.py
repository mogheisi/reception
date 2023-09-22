from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count, F, Sum, Avg
from django.db.models.functions import ExtractYear, ExtractMonth
from django.http import JsonResponse
from django.shortcuts import render, redirect

from util.charts import months, colorPrimary, colorSuccess, colorDanger, generate_color_palette, get_year_dict

from reception.models import Task, CustomerDevice, Problem


# @staff_member_required
def get_filter_options(request):
    grouped_purchases = Task.objects.annotate(year=ExtractYear("reception_datetime")).values("year").order_by("-year").distinct()
    options = [purchase["year"] for purchase in grouped_purchases]

    return JsonResponse({
        "options": options,
    })


@staff_member_required
def statistics_view(request):
    return render(request, "charts/statistics.html", {})


def receipt(request, pk):
    task = Task.objects.get(reception_no=pk)
    devices = CustomerDevice.objects.filter(task__reception_no=task.reception_no)
    problems = Problem.objects.filter(task__reception_no=task.reception_no)
    return render(request, 'reception/index.html', {'task': task, 'devices': devices, 'problems': problems})


def redirect_list(request):
    return redirect('reception/task/')
