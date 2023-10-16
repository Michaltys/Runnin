from django.contrib import admin
from django.urls import path, include
from Strava_integration import views as strava_views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', strava_views.landing_page, name='landing_page'),
    path('Runnin/get-refresh-token/', strava_views.get_refresh_token, name='get-refresh-token'),
    path('Runnin/list_athletes/', strava_views.list_athletes, name='list_athletes'),
    path('Runnin/activities_list/<int:athlete_id>/', strava_views.activities_list, name='activities_list'),
    path('Runnin/activity_details/<int:athlete_id>/activity/<int:activity_id>/', strava_views.activity_detail, name='activity_detail'),
    path('Runnin/activity/<int:activity_id>/comments', strava_views.activity_comments, name='activity_comments'),
    path('Runnin/update_activities', strava_views.update_activities, name='update_activities'),

]
