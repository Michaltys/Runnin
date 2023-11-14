from django.db import models
from django.contrib import admin




class Athlete(models.Model):
    #token fields
    refresh_token = models.CharField(max_length=255)
    access_token = models.CharField(max_length=255)
    expires_at = models.IntegerField()
    
    #athlete fields
    athlete_id = models.IntegerField(unique=True)
    firstname = models.CharField(max_length=50, null = True, blank = True)
    lastname = models.CharField(max_length=50, null = True, blank = True)
    city = models.CharField(max_length=50, null = True, blank = True)
    state = models.CharField(max_length=50, null = True, blank = True)
    country = models.CharField(max_length=20, null = True, blank = True)
    sex = models.CharField(max_length=5, null = True, blank = True)
    follower_count = models.IntegerField(null = True, blank = True)
    following_count = models.IntegerField(null = True, blank = True)



class Activity(models.Model):
    #general activity details used in the list of all activities
    athlete = models.ForeignKey('Athlete', on_delete=models.CASCADE, related_name="activities", db_column="athlete_id") 
    activity_id = models.BigIntegerField(unique=True)
    name = models.CharField(max_length=255, null = True, blank = True)
    activity_type = models.CharField(max_length=50)
    start_date = models.DateTimeField(null = True, blank = True)
    external_id = models.CharField(max_length=255, null = True, blank = True)
    upload_id = models.BigIntegerField(null=True, blank=True)
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
    start_latlng = models.CharField(max_length=255, null = True, blank = True) # GeoDjango to be considered
    end_latlng = models.CharField(max_length=255, null = True, blank = True) # GeoDjango to be considered
    calories = models.IntegerField(null = True, blank = True)
    has_heartrate = models.BooleanField(null=True, blank=True)
    achievement_count = models.IntegerField()
    kudos_count = models.IntegerField()
    comment_count = models.IntegerField()
    
    average_heartrate = models.FloatField(null=True, blank=True)
    average_temp = models.IntegerField(null=True, blank=True)
    has_kudoed = models.BooleanField(default=False)
    max_heartrate = models.FloatField(null=True, blank=True)
    pr_count = models.IntegerField(default=0, null = True, blank = True)
    total_photo_count = models.IntegerField(default=0)

class Comment(models.Model):
    athlete = models.ForeignKey(Athlete, on_delete=models.CASCADE)
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE, null=True)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

class Kudoers(models.Model):
    athlete = models.ForeignKey(Athlete, on_delete=models.CASCADE)
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE, null=True)
    kudoer = models.CharField(max_length=255)


    def __str__(self):
        return self.name




