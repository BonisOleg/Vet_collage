from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.views.generic import DetailView, ListView

from core.services.bunny import BunnyNetService
from .models import Webinar, WebinarRegistration


class WebinarListView(ListView):
    model = Webinar
    template_name = 'pages/webinars/list.html'
    context_object_name = 'webinars'
    paginate_by = 12

    def get_queryset(self):
        qs = Webinar.objects.filter(is_active=True)
        search = self.request.GET.get('q', '').strip()
        if search:
            qs = qs.filter(title__icontains=search)

        sort_map = {
            'price_asc': 'price',
            'price_desc': '-price',
            'newest': '-created_at',
        }
        sort = self.request.GET.get('sort', '')
        if sort in sort_map:
            qs = qs.order_by(sort_map[sort])

        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['search_query'] = self.request.GET.get('q', '')
        ctx['active_sort'] = self.request.GET.get('sort', '')
        ctx['sort_options'] = [
            ('newest', 'Найновіші'),
            ('price_asc', 'Ціна ↑'),
            ('price_desc', 'Ціна ↓'),
        ]
        return ctx


class WebinarDetailView(DetailView):
    model = Webinar
    template_name = 'pages/webinars/detail.html'
    context_object_name = 'webinar'

    def get_queryset(self):
        return Webinar.objects.filter(is_active=True)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        webinar = self.object
        user = self.request.user

        ctx['is_registered'] = False
        ctx['stripe_key'] = settings.STRIPE_PUBLISHABLE_KEY

        if user.is_authenticated:
            ctx['is_registered'] = WebinarRegistration.objects.filter(
                user=user, webinar=webinar,
            ).exists()

        return ctx


class WebinarWatchView(LoginRequiredMixin, DetailView):
    template_name = 'pages/webinars/watch.html'
    context_object_name = 'webinar'
    login_url = '/accounts/login/'

    def get_object(self, queryset=None):
        webinar = get_object_or_404(
            Webinar, slug=self.kwargs['slug'], is_active=True,
        )

        if not webinar.bunny_video_id:
            raise Http404('Запис вебінару ще не доступний')

        if not webinar.is_free:
            is_registered = WebinarRegistration.objects.filter(
                user=self.request.user, webinar=webinar,
            ).exists()
            if not is_registered:
                raise Http404('Доступ лише для зареєстрованих')

        return webinar

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        webinar = self.object

        library_id = webinar.bunny_library_id or settings.BUNNY_LIBRARY_ID
        if settings.BUNNY_TOKEN_AUTH_KEY:
            ctx['video_embed_url'] = BunnyNetService.generate_signed_url(
                video_id=webinar.bunny_video_id,
                library_id=library_id,
            )
        else:
            ctx['video_embed_url'] = BunnyNetService.get_embed_url(
                video_id=webinar.bunny_video_id,
                library_id=library_id,
                responsive=True,
            )

        return ctx
