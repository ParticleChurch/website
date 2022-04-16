from django.urls import path, include
import distributions.views

urlpatterns = [
    path("dll/", distributions.views.dll_download),
    
    path("injector/", distributions.views.injector_download),
    path("injector/version/", distributions.views.injector_version),
]