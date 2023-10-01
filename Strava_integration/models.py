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
    sex = models.CharField(max_length=5)


class Activity(models.Model):
    #general activity details used in the list of all activities
    athlete = models.ForeignKey('Athlete', on_delete=models.CASCADE, related_name="activities", db_column="athlete_id") 
    activity_id = models.BigIntegerField(unique=True)
    name = models.CharField(max_length=255)
    activity_type = models.CharField(max_length=50)
    start_date = models.DateTimeField()
    external_id = models.CharField(max_length=255)
    upload_id = models.BigIntegerField()
    athlete_count = models.IntegerField()
    resource_state = models.IntegerField()  #Resource state [int], indicates level of detail. Possible values: 1 -> "meta", 2 -> "summary", 3 -> "detail"
    photo_count = models.IntegerField()
    
    #specified - particular activity athletic details used
    distance = models.FloatField()
    moving_time = models.IntegerField() # [seconds]
    elapsed_time = models.IntegerField() # [seconds]
    average_speed = models.FloatField()
    max_speed = models.FloatField()
    average_cadence = models.FloatField(null=True, blank=True) # Ustawienie null=True i blank=True, ponieważ nie każda aktywność będzie miała kadencję
    total_elevation_gain = models.FloatField()
    start_latlng = models.CharField(max_length=255) # GeoDjango to be considered
    end_latlng = models.CharField(max_length=255) # GeoDjango to be considered
    calories = models.IntegerField()
    has_heartrate = models.BooleanField(null=True, blank=True)
    achievement_count = models.IntegerField()
    kudos_count = models.IntegerField()
    comment_count = models.IntegerField()
    
    
    def __str__(self):
        return self.name




