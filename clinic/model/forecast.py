from django.db import models

class Forecast(models.Model):
    Disease = models.CharField(max_length=100)
    Disease_count = models.IntegerField()
    DateAdded = models.DateField(blank=True)
    DateUpdated = models.DateField(auto_now_add=True)


    def __str__(self):
        return self.Disease