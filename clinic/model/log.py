from django.db import models
from django.utils.timezone import now

class Logbook(models.Model):
    username = models.CharField(max_length=100)
    desription = models.TextField(max_length=100,blank=True)
    DateAdded = models.DateField(auto_now_add=now)
    time = models.TimeField(auto_now_add=True)