from django.shortcuts import render, redirect
import requests
from .models import Athlete
from django.conf import settings

def create_athlete_instance(data):
    athlete_data = data.get("athlete")
    athlete_id = athlete_data.get("id")
    
    # Sprawdzanie, czy taki athlete już istnieje
    existing_athlete = Athlete.objects.filter(athlete_id=athlete_id).first()
    if existing_athlete:
        # Jeśli istnieje, możemy go aktualizować lub przekierować do innego widoku.
        return redirect('some_other_view_or_url_name')

    # Tworzenie nowego obiektu Athlete
    athlete = Athlete()
    athlete.refresh_token = data.get("refresh_token")
    athlete.access_token = data.get("access_token")
    athlete.expires_at = data.get("expires_at")
    athlete.athlete_id = athlete_id
    athlete.firstname = athlete_data.get("firstname")
    athlete.lastname = athlete_data.get("lastname")
    athlete.city = athlete_data.get("city")
    athlete.state = athlete_data.get("state")
    athlete.country = athlete_data.get("country")
    athlete.sex = athlete_data.get("sex")
    athlete.save()

def get_refresh_token(request):
    if request.method == "POST":
        authorization_code = request.POST.get('authorization_code')
        
        if not authorization_code:
            return render(request, 'Runnin/code_input.html', {'error': 'Authorization code not provided'})

        payload = {
            'client_id': settings.STRAVA_CLIENT_ID,
            'client_secret': settings.STRAVA_CLIENT_SECRET,
            'code': authorization_code, 
            'grant_type': 'authorization_code'
        }
        
        STRAVA_TOKEN_URL = settings.AUTH_URL
        response = requests.post(STRAVA_TOKEN_URL, data=payload, verify=True)

        data = response.json()
        create_athlete_instance(data)
    
    return render(request, 'Runnin/code_input.html')

def list_athletes(request):
    athletes = Athlete.objects.all()
    return render(request, 'Runnin/athlete_list.html', {'athletes': athletes})
