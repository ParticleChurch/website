from django.urls import path, include
import particle_sessions.views

urlpatterns = [
    path("", particle_sessions.views.particle_sessions),
    path("<str:session_id>/", particle_sessions.views.particle_session),
]