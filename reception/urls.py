from django.contrib import admin
from django.urls import path
from reception.views import receipt, redirect_list, get_filter_options, statistics_view
from django.conf.urls.static import static
from django.conf import settings


urlpatterns = [
    path('chart/filter-options/', get_filter_options, name="chart-filter-options"),
    path('receipt/<int:pk>/', receipt, name='receipt'),
    path('task/', redirect_list, name='redirect_list'),
    path("statistics/", statistics_view, name="shop-statistics"),  # new

]
