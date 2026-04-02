from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('checkout/', views.create_checkout_view, name='checkout'),
    path('webhook/stripe/', views.stripe_webhook_view, name='stripe_webhook'),
]
