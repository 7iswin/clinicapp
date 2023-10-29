from django.urls import path
from clinic.view import forecastAndAnalytic
app_name='forecastingAndAnalytic'
urlpatterns = [
    path('',forecastAndAnalytic.index,name='index'),

]
