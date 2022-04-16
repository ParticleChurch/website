from rest_framework import serializers
from users.models import *

from particle_api.helpers import TimestampField

class UserSerializer(serializers.ModelSerializer):
    time_registered = TimestampField()
    time_subscription_form_succeeded = TimestampField()
    subscription_period_end = TimestampField()
    
    class Meta:
        model = User
        fields = [
            'user_id',
            'stripe_customer_id',
            'time_registered',
            'subscription_status',
            'time_subscription_form_succeeded',
            'subscription_period_end',
            'stripe_subscription_id',
        ]