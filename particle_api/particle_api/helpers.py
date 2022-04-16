from rest_framework import serializers
import datetime
import hashlib
import string
import random
import stripe
import json
from ipware import get_client_ip

with open("/var/www/particle_api/.secrets-particle.church", "r") as f:
    SECRETS = json.load(f)

stripe.api_key = SECRETS['stripe_live_key']

character_pool_62 = string.ascii_lowercase + string.ascii_uppercase + string.digits
def random_string(length):
    return ''.join(random.choices(character_pool_62, k = length))

def generate_session_id():
    return random_string(32)

def hash_password(password, salt):
    return hashlib.pbkdf2_hmac(
        "sha512",
        hashlib.sha256(str(password).encode("utf-8")).digest(),
        str(salt).encode("utf-8"),
        10_000 # roughly 8 ms per hash
    ).hex()

class TimestampField(serializers.Field):
    def to_representation(self, value):
        return value.timestamp()
    
    def to_internal_value(self, value):
        return datetime.datetime.utcfromtimestamp(value)

class SignedIntConverter:
    regex = '-?\d+'

    def to_python(self, value):
        return int(value)

    def to_url(self, value):
        return f'{value:d}'

# discord integration
import importlib.util
message_manager_spec = importlib.util.spec_from_file_location("message_manager", "/var/www/particle_bot/message_manager.py")
message_manager = importlib.util.module_from_spec(message_manager_spec)
message_manager_spec.loader.exec_module(message_manager)

REQUEST_ENTRY_IP = '0.0.0.0'
class IPLoggerMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        global REQUEST_ENTRY_IP
        ip, routable = get_client_ip(request)
        if ip is not None:
            REQUEST_ENTRY_IP = ip
        
        return self.get_response(request)

def log_message(message_type, user = None, session = None, **kwargs):
    if user is not None:
        kwargs["user"] = {
            "id": user.user_id,
            "link": f"https://api.particle.church/admin/users/user/{user.user_id}",
            "stripe_id": user.stripe_customer_id,
            "stripe_link": f"https://dashboard.stripe.com/customers/{user.stripe_customer_id}",
            "email": user.email,
            "subscribed": user.is_subscribed(),
        }
    
    if session is not None:
        kwargs["session"] = {
            "id": session.session_id,
            "link": f"https://api.particle.church/admin/particle_sessions/particlesession/{session.session_id}",
            "user_id": session.user_id,
            "user_link": f"https://api.particle.church/admin/users/user/{session.user_id}",
            "platform": session.platform,
        }
    
    kwargs['ip'] = kwargs.get('ip', REQUEST_ENTRY_IP)
    
    return message_manager.send_message(message_type, **kwargs)