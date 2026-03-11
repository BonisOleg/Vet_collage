from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView
from .models import Course, Category


class CourseListView(ListView):
    model = Course
    template_name = 'pages/courses/list.html'
    context_object_name = 'courses'
    paginate_by = 12

    def get_queryset(self):
        qs = Course.objects.filter(is_active=True).select_related('category')
        category = self.request.GET.get('category')
        level = self.request.GET.get('level')
        sort = self.request.GET.get('sort', '')

        if category:
            qs = qs.filter(category__slug=category)
        if level:
            qs = qs.filter(level=level)

        sort_map = {
            'price_asc': 'price',
            'price_desc': '-price',
            'newest': '-created_at',
            'popular': '-is_popular',
        }
        if sort in sort_map:
            qs = qs.order_by(sort_map[sort])

        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['categories'] = Category.objects.all()
        ctx['active_category'] = self.request.GET.get('category', '')
        ctx['active_level'] = self.request.GET.get('level', '')
        ctx['active_sort'] = self.request.GET.get('sort', '')
        ctx['levels'] = Course.LEVEL_CHOICES
        ctx['sort_options'] = [
            ('newest', 'Найновіші'),
            ('price_asc', 'Ціна ↑'),
            ('price_desc', 'Ціна ↓'),
            ('popular', 'Популярні'),
        ]
        if self.request.headers.get('HX-Request'):
            self.template_name = 'pages/courses/partials/course_grid.html'
        return ctx


class CourseDetailView(DetailView):
    model = Course
    template_name = 'pages/courses/detail.html'
    context_object_name = 'course'
