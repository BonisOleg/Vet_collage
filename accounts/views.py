from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.views.decorators.http import require_POST
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        is_htmx = request.headers.get('HX-Request')

        if user:
            login(request, user)
            if is_htmx:
                response = HttpResponse(status=200)
                response['HX-Redirect'] = request.POST.get('next', '/')
                return response
            return redirect(request.POST.get('next', '/'))
        else:
            if is_htmx:
                return render(request, 'components/forms/login_form.html', {
                    'error': 'Невірний email або пароль'
                })
            return render(request, 'components/forms/login_form.html', {
                'error': 'Невірний email або пароль'
            })

    return render(request, 'pages/accounts/login.html')


def register_step1_view(request):
    if request.method == 'POST':
        request.session['reg_first_name'] = request.POST.get('first_name', '')
        request.session['reg_last_name'] = request.POST.get('last_name', '')
        request.session['reg_email'] = request.POST.get('email', '')
        request.session['reg_password'] = request.POST.get('password1', '')
        return render(request, 'components/forms/register_step2_form.html')
    return render(request, 'pages/accounts/register.html')


def register_step2_view(request):
    if request.method == 'POST':
        from django.contrib.auth.models import User
        email = request.session.get('reg_email', '')
        password = request.session.get('reg_password', '')
        first_name = request.session.get('reg_first_name', '')
        last_name = request.session.get('reg_last_name', '')

        if User.objects.filter(email=email).exists():
            return render(request, 'components/forms/register_form.html', {
                'error': 'Користувач з таким email вже існує'
            })

        user = User.objects.create_user(
            username=email, email=email, password=password,
            first_name=first_name, last_name=last_name
        )
        login(request, user)

        is_htmx = request.headers.get('HX-Request')
        if is_htmx:
            response = HttpResponse(status=200)
            response['HX-Redirect'] = '/cabinet/'
            return response
        return redirect('accounts:cabinet')

    return render(request, 'components/forms/register_step2_form.html')


def logout_view(request):
    logout(request)
    return redirect('core:home')


def password_reset_view(request):
    if request.method == 'POST':
        return render(request, 'components/forms/password_reset_sent.html')
    return render(request, 'components/forms/password_reset_form.html')


class CabinetView(LoginRequiredMixin, TemplateView):
    template_name = 'pages/accounts/cabinet.html'
    login_url = '/accounts/login/'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['active_tab'] = self.request.GET.get('tab', 'profile')
        return ctx
