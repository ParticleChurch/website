from django.urls import path, include
import stripe_webhooks.views

urlpatterns = [
    path("subscription_updated/", stripe_webhooks.views.subscription_updated),
]