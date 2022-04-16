from rest_framework.response import Response
from rest_framework.decorators import api_view, authentication_classes
import particle_api.helpers as helpers

from particle_sessions.models import *
from particle_sessions.serializers import *

from users.models import *
from users.serializers import *

import datetime

@api_view(['GET'])
def particle_session(request, session_id):
    if len(session_id) != 32:
        return Response({ "detail": "Every session id must be 32 characters long."}, status = 400)
    
    if not set(session_id).issubset(set(helpers.session_id_character_pool)):
        return Response({ "detail": "Session ids may only contain [a-zA-Z0-9]." }, status = 400)
    
    try:
        session = ParticleSession.objects.get(session_id = session_id)
    except ParticleSession.DoesNotExist as e:
        return Response({ "detail": f"No session was found with session_id = `{session_id}`." }, status = 404)
    
    if session.time_closed:
        return Response({ "detail": f"That session has been closed. Please open a new one." }, status = 401)
    
    if datetime.datetime.now() >= session.time_opened + datetime.timedelta(days = 60):
        return Response({ "detail": f"That session timed out since it was opened over 60 days ago. Please open a new one." }, status = 401)
    
    return Response(ParticleSessionSerializer(session).data)

@api_view(['POST'])
def particle_sessions(request):
    email = request.data.get("email", "").lower().replace(" ", "")
    password = request.data.get("password", "").strip()
    platform = request.data.get("platform", "").strip()
    
    if not email or not password:
        return Response({ "detail": "You must supply both an email and a password." }, status = 400)
    
    if platform not in ("web", "injector"):
        return Response({ "detail": "Invalid platform." }, status = 400)
    
    try:
        user = User.objects.get(email = email)
    except User.DoesNotExist as e:
        return Response({ "detail": "Invalid Email." }, status = 404)
    
    password_hash = helpers.hash_password(password, user.password_salt)
    if password_hash != user.password_hash:
        return Response({ "detail": "Incorrect Password." }, status = 401)
    
    session = ParticleSession(
        session_id = helpers.generate_session_id(),
        user_id = user.user_id,
        platform = platform
    )
    session.save()
    
    helpers.log_message(
        'login',
        user = user,
        session = session
    )
    
    return Response(ParticleSessionSerializer(session).data)