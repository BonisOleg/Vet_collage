from django.shortcuts import render
from django.views.generic import TemplateView
from .models import MembershipPlan


class MembershipIndexView(TemplateView):
    template_name = 'pages/membership/index.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['plans'] = MembershipPlan.objects.all()
        return ctx
