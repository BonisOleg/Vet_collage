from __future__ import annotations

from django.contrib.auth import authenticate, get_user_model, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordResetForm
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.views.generic import TemplateView

from courses.models import Course, Enrollment
from payments.models import Order
from webinars.models import Webinar, WebinarRegistration

User = get_user_model()


def login_view(request: HttpRequest) -> HttpResponse:
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
            ctx = {'error': 'Невірний email або пароль'}
            return render(request, 'components/forms/login_form.html', ctx)

    return render(request, 'pages/accounts/login.html')


def register_step1_view(request: HttpRequest) -> HttpResponse:
    if request.method == 'POST':
        request.session['reg_first_name'] = request.POST.get('first_name', '')
        request.session['reg_last_name'] = request.POST.get('last_name', '')
        request.session['reg_email'] = request.POST.get('email', '')
        request.session['reg_password'] = request.POST.get('password1', '')
        return render(request, 'components/forms/register_step1_success.html')
    return render(request, 'pages/accounts/register.html')


def register_step2_view(request: HttpRequest) -> HttpResponse:
    if request.method == 'POST':
        email = request.session.get('reg_email', '')
        password = request.session.get('reg_password', '')
        first_name = request.session.get('reg_first_name', '')
        last_name = request.session.get('reg_last_name', '')

        if User.objects.filter(email=email).exists():
            return render(request, 'components/forms/register_form.html', {
                'error': 'Користувач з таким email вже існує',
            })

        user = User.objects.create_user(
            username=email, email=email, password=password,
            first_name=first_name, last_name=last_name,
        )
        login(request, user)

        is_htmx = request.headers.get('HX-Request')
        if is_htmx:
            response = HttpResponse(status=200)
            response['HX-Redirect'] = '/accounts/cabinet/'
            return response
        return redirect('accounts:cabinet')

    return render(request, 'components/forms/register_step1_success.html')


def logout_view(request: HttpRequest) -> HttpResponse:
    logout(request)
    return redirect('core:home')


def password_reset_view(request: HttpRequest) -> HttpResponse:
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        if email:
            form = PasswordResetForm({'email': email})
            if form.is_valid():
                form.save(
                    request=request,
                    use_https=request.is_secure(),
                    from_email=None,
                    email_template_name='registration/password_reset_email.html',
                    subject_template_name='registration/password_reset_subject.txt',
                )
        return render(request, 'components/forms/password_reset_sent.html')
    return render(request, 'components/forms/password_reset_form.html')


@login_required(login_url='/accounts/login/')
def password_change_view(request: HttpRequest) -> HttpResponse:
    if request.method == 'POST':
        user = request.user
        old_password = request.POST.get('old_password', '')
        new_password1 = request.POST.get('new_password1', '')
        new_password2 = request.POST.get('new_password2', '')

        error = None
        if not user.check_password(old_password):
            error = 'Поточний пароль невірний'
        elif not new_password1:
            error = 'Введіть новий пароль'
        elif new_password1 != new_password2:
            error = 'Паролі не збігаються'
        elif len(new_password1) < 8:
            error = 'Пароль повинен містити мінімум 8 символів'

        if error:
            return render(request, 'pages/accounts/partials/password_change_error.html', {
                'error': error,
            })

        user.set_password(new_password1)
        user.save()
        from django.contrib.auth import update_session_auth_hash
        update_session_auth_hash(request, user)

        return render(request, 'pages/accounts/partials/password_change_success.html')

    return redirect('accounts:cabinet')


@login_required(login_url='/accounts/login/')
def profile_update_view(request: HttpRequest) -> HttpResponse:
    if request.method == 'POST':
        user = request.user
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)

        new_email = request.POST.get('email', '').strip()
        if new_email and new_email != user.email:
            if not User.objects.filter(email=new_email).exclude(pk=user.pk).exists():
                user.email = new_email
                user.username = new_email

        user.save()

        is_htmx = request.headers.get('HX-Request')
        if is_htmx:
            return render(request, 'pages/accounts/partials/profile_success.html')
        return redirect('accounts:cabinet')

    return redirect('accounts:cabinet')


class CabinetView(LoginRequiredMixin, TemplateView):
    template_name = 'pages/accounts/cabinet.html'
    login_url = '/accounts/login/'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        user = self.request.user
        tab = self.request.GET.get('tab', 'account') or 'account'
        ctx['active_tab'] = tab

        enrollments = Enrollment.objects.filter(
            user=user,
        ).select_related('course', 'course__category')
        enrolled_courses = [e.course for e in enrollments]
        if enrolled_courses:
            ctx['user_courses'] = enrolled_courses
        else:
            slug_fallback = getattr(
                settings, 'CABINET_CONTINUE_FALLBACK_COURSE_SLUGS', (),
            ) or ()
            if slug_fallback:
                slug_order = {s: i for i, s in enumerate(slug_fallback)}
                qs = (
                    Course.objects.filter(is_active=True, slug__in=slug_fallback)
                    .select_related('category')
                )
                ctx['user_courses'] = sorted(
                    qs, key=lambda c: slug_order[c.slug],
                )[:2]
            else:
                ctx['user_courses'] = list(
                    Course.objects.filter(is_active=True, is_popular=True).select_related(
                        'category',
                    )[:2],
                )

        registrations = WebinarRegistration.objects.filter(
            user=user,
        ).select_related('webinar')
        user_webinars = [r.webinar for r in registrations]
        ctx['user_webinars'] = user_webinars

        if not user_webinars:
            ctx['recommended_webinars'] = list(
                Webinar.objects.filter(is_active=True).order_by('-created_at')[:2]
            )
        else:
            ctx['recommended_webinars'] = []

        ctx['user_membership'] = None
        if hasattr(user, 'membership'):
            try:
                ctx['user_membership'] = user.membership
            except Exception:
                pass

        ctx['orders'] = Order.objects.filter(
            user=user,
        ).order_by('-created_at')[:20]

        return ctx
