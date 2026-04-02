from django.urls import path
from . import views

app_name = 'courses'

urlpatterns = [
    path('', views.CourseListView.as_view(), name='list'),
    path('<slug:slug>/', views.CourseDetailView.as_view(), name='detail'),
    path('<slug:slug>/learn/', views.CourseOverviewView.as_view(), name='overview'),
    path(
        '<slug:course_slug>/lessons/<slug:lesson_slug>/',
        views.LessonView.as_view(),
        name='lesson',
    ),
]
