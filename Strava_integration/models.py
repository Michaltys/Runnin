from django.db import models
from django.contrib import admin







class Athlete(models.Model):
    refresh_token = models.CharField(max_length=255)
    access_token = models.CharField(max_length=255)
    expires_at = models.IntegerField()
    athlete_id = models.IntegerField(unique=True)
    firstname = models.CharField(max_length=50)
    lastname = models.CharField(max_length=50)
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    country = models.CharField(max_length=20)
    sex = models.CharField(max_length=10)


