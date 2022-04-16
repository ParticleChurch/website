from django.urls import path, include
import upload.views

urlpatterns = [
    path("dll/", upload.views.upload_dll),
    #path("injector/", upload.views.upload_injector),
]