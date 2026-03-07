from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView
from .models import Course, Category


class CourseListView(ListView):
    model = Course
    template_name = 'pages/courses/list.html'
    context_object_name = 'courses'
    paginate_by = 12

    def get_queryset(self):
        qs = Course.objects.filter(is_active=True)
        category = self.request.GET.get('category')
        if category:
            qs = qs.filter(category__slug=category)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['categories'] = Category.objects.all()
        ctx['active_category'] = self.request.GET.get('category', '')
        if self.request.headers.get('HX-Request'):
            self.template_name = 'pages/courses/partials/course_grid.html'
        return ctx


class CourseDetailView(DetailView):
    model = Course
    template_name = 'pages/courses/detail.html'
    context_object_name = 'course'
