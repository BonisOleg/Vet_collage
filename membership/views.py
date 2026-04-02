from django.views.generic import TemplateView
from .models import MembershipPlan, UserMembership


class MembershipPlansView(TemplateView):
    """Публічна сторінка тарифних планів — /membership/plans/"""
    template_name = 'pages/membership/index.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['plans'] = MembershipPlan.objects.all()
        return ctx


class MembershipDashboardView(TemplateView):
    """Сторінка «Мій статус членства» — /membership/ (той самий layout для всіх)."""
    template_name = 'pages/membership/dashboard.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        user = self.request.user
        ctx['user_membership'] = None
        if user.is_authenticated:
            try:
                ctx['user_membership'] = user.membership
            except UserMembership.DoesNotExist:
                pass
        return ctx
