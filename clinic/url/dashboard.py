from django.urls import path
app_name='dashboard'
from clinic.view import dashboard
urlpatterns = [
    path('',dashboard.index,name='index'),
    path('excel',dashboard.ExcelFileUpload,name='excel'),
    path('update_chart',dashboard.update_chart,name='update_chart'),
    path('update_forecast',dashboard.update_forecast,name='update_forecast'),

]
