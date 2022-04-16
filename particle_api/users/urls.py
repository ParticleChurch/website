from django.urls import path, include
import users.views

urlpatterns = [
    path("", users.views.user),
    path("email/<str:email>/", users.views.user_by_email),
    path("unsubscribe/", users.views.unsubscribe),
    path("subscribe/", users.views.generate_checkout_url),
]