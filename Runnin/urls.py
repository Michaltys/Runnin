from django.contrib import admin
from django.urls import path, include
from Strava_integration import views as strava_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('Runnin/get-refresh-token/', strava_views.get_refresh_token, name='get-refresh-token'),
]
