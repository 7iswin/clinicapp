from django.contrib import admin
from django.urls import path,include
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    path('admin/', admin.site.urls),
    path('account/',include('clinic.url.account')),
    path('',include('clinic.url.dashboard')),
    path('forecastingAndAnalytic/',include('clinic.url.forecastAndAnalytic')),
    path('studentRecord/',include('clinic.url.studentRecord')),

]
urlpatterns = urlpatterns+static(settings.MEDIA_URL,
document_root=settings.MEDIA_ROOT)

