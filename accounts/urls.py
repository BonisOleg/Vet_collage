from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_step1_view, name='register_step1'),
    path('register/step2/', views.register_step2_view, name='register_step2'),
    path('password-reset/', views.password_reset_view, name='password_reset'),
    path('cabinet/', views.CabinetView.as_view(), name='cabinet'),
]
