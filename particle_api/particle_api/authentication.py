from django.contrib.auth.models import AnonymousUser
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.conf import settings
from ipware import get_client_ip

class NoAuthentication(BaseAuthentication):
    def authenticate(self):
        return (AnonymousUser(), None)

class ParticleAuthentication(BaseAuthentication):
    def authenticate(self):
        # TODO: ACTUALLY AUTHENTICATE
        return (AnonymousUser(), None)