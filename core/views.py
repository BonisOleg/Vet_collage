from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.views.generic import TemplateView
from django.contrib import messages


class HomeView(TemplateView):
    template_name = 'pages/core/home.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['popular_courses'] = []
        ctx['membership_plans'] = []
        ctx['services'] = []
        ctx['about_cards'] = []
        return ctx


class AboutView(TemplateView):
    template_name = 'pages/core/about.html'


def contact_view(request):
    if request.method == 'POST':
        name = request.POST.get('name', '')
        email = request.POST.get('email', '')
        phone = request.POST.get('phone', '')
        message = request.POST.get('message', '')

        if request.htmx if hasattr(request, 'htmx') else request.headers.get('HX-Request'):
            return HttpResponse(
                '<p style="color:var(--color-dark); font-weight:600;">\u2713 \u0414\u044f\u043a\u0443\u0454\u043c\u043e! \u041c\u0438 \u0437\u0432\u02bc\u044f\u0436\u0435\u043c\u043e\u0441\u044c \u0437 \u0432\u0430\u043c\u0438 \u043d\u0430\u0439\u0431\u043b\u0438\u0436\u0447\u0438\u043c \u0447\u0430\u0441\u043e\u043c.</p>'
            )
        messages.success(request, 'Дякуємо за повідомлення!')
        return redirect('core:home')

    return render(request, 'pages/core/contact.html')
