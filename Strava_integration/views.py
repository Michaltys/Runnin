from django.shortcuts import render
import requests
from django.conf import settings
from django.http import JsonResponse, HttpResponseRedirect

def get_refresh_token(request):
    authorization_code = None

    if request.method == "POST":
        authorization_code = request.POST.get('authorization_code')
        
        if not authorization_code:
            # Failure communicate, suggesting to run it again
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
        refresh_token = data.get("refresh_token")
        access_token = data.get("access_token")
        expires_at = data.get("expires_at")
        athlete = data.get("athlete")

        return JsonResponse({
            'refresh_token': refresh_token,
            'access_token': access_token,
            'expires_at': expires_at,
            'athlete': athlete
        })
    
    return render(request, 'Runnin/code_input.html')
