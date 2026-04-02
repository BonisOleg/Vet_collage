from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('about/', views.AboutView.as_view(), name='about'),
    path('contact/', views.contact_view, name='contact'),
    path('newsletter/', views.newsletter_view, name='newsletter'),
    path('payment/success/', views.PaymentSuccessView.as_view(), name='payment_success'),
    path('payment/failure/', views.PaymentFailureView.as_view(), name='payment_failure'),
    path('privacy/', views.PrivacyView.as_view(), name='privacy'),
    path('cookies/', views.CookiesView.as_view(), name='cookies'),
]
