from django.urls import path
from . import views

app_name = 'webinars'

urlpatterns = [
    path('', views.WebinarListView.as_view(), name='list'),
    path('<slug:slug>/', views.WebinarDetailView.as_view(), name='detail'),
    path('<slug:slug>/watch/', views.WebinarWatchView.as_view(), name='watch'),
]
