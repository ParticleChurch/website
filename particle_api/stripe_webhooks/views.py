from datetime import datetime

from rest_framework.response import Response
from rest_framework.decorators import api_view, authentication_classes
import particle_api.helpers as helpers

from users.models import *

endpoint_secret = 'whsec_dwXz5ZPWKcIrG8G0Q6ccrhZXHOIQZBaI'

# Create your views here.
@api_view(['POST'])
def subscription_updated(request):
    event = helpers.stripe.Webhook.construct_event(
        request.body,
        request.headers.get('STRIPE_SIGNATURE'),
        helpers.SECRETS['stripe_subscription_update_webhook_key']
    )
    
    object = request.data.get("data", {}).get("object", {})
    subscription_id = object.get("id")
    customer_id = object.get("customer")
    subscription_status = object.get("status")
    current_period_end = object.get("current_period_end")
    
    try:
        current_period_end = float(current_period_end)
    except:
        current_period_end = None
    
    if not all((subscription_id, customer_id, subscription_status, current_period_end)):
        return Response({
            "success": False,
            "interpreted_customer_id": customer_id,
            "interpreted_subscription_status": subscription_status,
            "interpreted_current_period_end": current_period_end,
            "object": object
        }, status = 400)
    
    user = User.objects.filter(stripe_customer_id = customer_id).first()
    
    if not user:
        return Response({"success": False, "interpreted_customer_id": customer_id}, status = 404)
    
    user.subscription_status = subscription_status
    user.subscription_period_end = datetime.utcfromtimestamp(current_period_end)
    user.stripe_subscription_id = subscription_id
    user.save()
    
    return Response({"success": True, "new_status": subscription_status})