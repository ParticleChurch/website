from datetime import datetime, timedelta

from django.db import transaction

from rest_framework.response import Response
from rest_framework.decorators import api_view, authentication_classes
import particle_api.helpers as helpers

from email_validator import validate_email, EmailNotValidError

from particle_sessions.models import *
from particle_sessions.serializers import *
from users.models import *
from users.serializers import *

@api_view(['POST'])
def user(request):
    email = request.data.get("email", "").lower().replace(" ", "")
    password = request.data.get("password", "").strip()
    
    if not email or not password:
        return Response({ "detail": "You must supply both an email and a password." }, status = 400)
    
    if len(password) < 6:
        return Response({ "detail": f"Password is too short. Must be at least 6 characters." }, status = 400)
    
    try:
        valid = validate_email(email)
        email = valid.email
    except EmailNotValidError as e:
        return Response({ "detail": f"Invalid Email: {e}" }, status = 400)
    
    with transaction.atomic():
        password_salt = helpers.random_string(64)
        user = User(
            email = email,
            password_salt = password_salt,
            password_hash = helpers.hash_password(password, password_salt),
            stripe_customer_id = "unknown",
        )
        user.save()
        
        customer = helpers.stripe.Customer.create(
            email = email,
            metadata = {
                "user_id": user.user_id
            },
        )
        user.stripe_customer_id = customer.id
        
        user.save()
    
    session = ParticleSession(
        session_id = helpers.generate_session_id(),
        user_id = user.user_id
    )
    session.save()
    return Response(ParticleSessionSerializer(session).data)

@api_view(['GET'])
def user_by_email(request, email):
    try:
        user = User.objects.get(email = email)
    except User.DoesNotExist as e:
        return Response({ "registered": False })
    return Response({ "registered": True })

@api_view(['GET'])
def unsubscribe(request):
    session = ParticleSession.objects.filter(
        session_id = request.COOKIES.get("session_id"),
        time_opened__gt = datetime.now() - timedelta(days = 14),
        time_closed__isnull = True
    ).first()
    
    if not session:
        return Response({ "detail": "You must have an active session." }, status = 400)
    
    user = User.objects.get(user_id = session.user_id)
    
    if user.stripe_subscription_id:
        stripe_result = helpers.stripe.Subscription.delete(user.stripe_subscription_id)
        user.stripe_subscription_id = None
    
    user.subscription_status = None
    user.time_subscription_form_succeeded = None
    user.subscription_period_end = None
    user.save()
    
    return Response({"success": True, "user": UserSerializer(user).data})

@api_view(['GET'])
def generate_checkout_url(request):
    session = ParticleSession.objects.filter(
        session_id = request.COOKIES.get("session_id"),
        time_opened__gt = datetime.now() - timedelta(days = 14),
        time_closed__isnull = True
    ).first()
    
    if not session:
        return Response({ "detail": "You must have an active session." }, status = 400)
    
    user = User.objects.get(user_id = session.user_id)
    
    pending_checkout = PendingCheckout(
        checkout_id = helpers.generate_session_id(),
        user_id = user.user_id
    )
    
    session = helpers.stripe.checkout.Session.create(
        line_items = [{ 'price': 'price_1KQAieFaMsHR3sNORnOC4qSU', 'quantity': 1 }],
        customer = user.stripe_customer_id,
        mode = 'subscription',
        success_url = f'https://particle.church/subscription_checkout?result=success&checkout_id={pending_checkout.checkout_id}',
        cancel_url = f'https://particle.church/subscription_checkout?result=cancel&checkout_id={pending_checkout.checkout_id}'
    )
    
    pending_checkout.stripe_session_id = session.id
    pending_checkout.save()
    
    return Response({ "url": session.url })