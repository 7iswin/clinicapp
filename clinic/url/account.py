from django.urls import path,include
from clinic.view import account
app_name = 'account'
urlpatterns = [
    path('',account.index,name='index'),
    path('login/',account.login,name='login'),
    path('logout/',account.logout,name='logout'),
    path('profile/', account.profile,name='profile'),
    path('edit_profile/', account.edit_profile,name='edit_profile'),
    path('change_password/', account.change_password,name='change_password'),
    path('generate_and_send_otp/',account.generate_and_send_otp,name='generate_and_send_otp'),
    # path('role_permissions/', account.role_permissions,name='role_permissions'),
    
]