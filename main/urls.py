from django.urls import path
from django.urls.conf import include
from . import views

urlpatterns = [
    path('', views.main_page),
    path('register', views.register),
    path('graphics', views.test),  # graphics
    path('report', views.report_page),
    path('report_data', views.report_data),
    path('report_data1', views.report_data1),
    path('report_symptom', views.report_symptom),
    path('report_symptoms_count', views.report_symptoms_count),
    path('report_ASH_count', views.report_ASH_count),
    path('without_reports', views.get_without_reports),
    path('uncalled_reports', views.get_uncalled_reports),
    path('reports_more_three', views.get_reports_with_triple_symptoms),
    path('reports_symptom_three_days',
         views.get_reports_with_symptom_three_days),
    path('report_all', views.report_all),
    path('report_health', views.report_health),
    path('report_sick', views.report_sick),
    path('download_excel_file/', views.download_excel_file),
    path('test', views.test),
]
