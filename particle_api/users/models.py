from django.db import models
from datetime import datetime, timezone

class User(models.Model):
    user_id = models.BigAutoField(primary_key = True)
    stripe_customer_id = models.TextField(blank = False, null = False)
    
    time_registered = models.DateTimeField(auto_now_add = True)
    
    email = models.CharField(unique = True, max_length = 128)
    password_hash = models.CharField(max_length = 128)
    password_salt = models.CharField(max_length = 64, blank = False, null = False)
    
    subscription_status = models.TextField(blank = True, null = True, default = None)
    time_subscription_form_succeeded = models.DateTimeField(null = True, default = None)
    subscription_period_end = models.DateTimeField(null = True, default = None)
    stripe_subscription_id = models.TextField(blank = True, null = True, default = None)
    
    def is_subscribed(self):
        recently_submitted_payment = self.time_subscription_form_succeeded and (datetime.now(timezone.utc) - self.time_subscription_form_succeeded).total_seconds() <= 120
        active_subscription = self.subscription_status == "active"
        subscription_ended = self.subscription_period_end and (datetime.now(timezone.utc) - self.subscription_period_end).total_seconds() >= 86400 * 2
        
        return (recently_submitted_payment or active_subscription) and not subscription_ended
    
    class Meta:
        ordering = ['user_id']

class PendingCheckout(models.Model):
    checkout_id = models.CharField(primary_key = True, blank = False, null = False, max_length = 32)
    user_id = models.BigIntegerField(blank = False, null = False)
    time_opened = models.DateTimeField(auto_now_add = True)
    time_closed = models.DateTimeField(blank = True, null = True, default = None)
    result = models.CharField(blank = True, null = True, max_length = 16, default = None)
    
    stripe_session_id = models.TextField(blank = True, null = True, default = None)
    