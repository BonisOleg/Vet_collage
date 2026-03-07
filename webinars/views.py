from django.views.generic import ListView, DetailView
from .models import Webinar


class WebinarListView(ListView):
    model = Webinar
    template_name = 'pages/webinars/list.html'
    context_object_name = 'webinars'
    paginate_by = 12

    def get_queryset(self):
        return Webinar.objects.filter(is_active=True)


class WebinarDetailView(DetailView):
    model = Webinar
    template_name = 'pages/webinars/detail.html'
    context_object_name = 'webinar'
