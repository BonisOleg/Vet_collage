from django.urls import path
from . import views

app_name = 'membership'

urlpatterns = [
    path('', views.MembershipDashboardView.as_view(), name='index'),
    path('plans/', views.MembershipPlansView.as_view(), name='plans'),
]
