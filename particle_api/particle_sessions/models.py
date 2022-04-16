from django.db import models

# Create your models here.
class ParticleSession(models.Model):
    session_id = models.CharField(primary_key = True, unique = True, max_length = 32)
    
    time_opened = models.DateTimeField(auto_now_add = True)
    time_last_seen = models.DateTimeField(auto_now = True)
    time_closed = models.DateTimeField(null = True, blank = True)
    
    user_id = models.BigIntegerField()
    platform = models.CharField(blank = True, null = True, default = None, max_length = 32)
    
    class Meta:
        ordering = ['-time_last_seen']