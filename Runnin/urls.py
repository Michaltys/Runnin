from django.contrib import admin
from django.urls import path, include
from Strava_integration import views as strava_views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('Runnin/get-refresh-token/', strava_views.get_refresh_token, name='get-refresh-token'),
    path('Runnin/list_athletes/', strava_views.list_athletes, name='list_athletes'),
    path('Runnin/activities_list/<int:athlete_id>/', strava_views.activities_list, name='activities_list'),

    #path('Runnin/activity_list/<int:athlete_id>/', strava_views.activity_list_view, name='activity_list'),
    #path('Runnin/activity_detail/<int:athlete_id>/', strava_views.activity_detail, name='activity_detail'),
    #path('')
]
