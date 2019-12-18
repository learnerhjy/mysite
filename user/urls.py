from django.urls import path
from . import views
urlpatterns = [
    path('login/',views.login,name='login'),
    path('login_for_modal/<status>',views.login_for_modal,name='login_for_modal'),
    path('register/',views.register,name='register'),
    path('logout/',views.logout,name='logout'),
    path('user_info/<int:user_pk>',views.user_info,name='user_info'),
    path('change_nickname',views.change_nickname,name='change_nickname'),
    path('bind_email',views.bind_email,name='bind_email'),
    path('send_validation_code',views.send_validation_code,name='send_validation_code'),
    path('change_password',views.change_password,name='change_password'),
    path('reset_password',views.reset_password,name='reset_password'),
    path('user_config',views.user_config,name='user_config'),
]