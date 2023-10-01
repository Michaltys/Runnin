from django.shortcuts import render, redirect, get_object_or_404
import requests
from Strava_integration.models import Athlete, Activity
from django.conf import settings

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

def create_athlete_instance(data):
    athlete_data = data.get("athlete")
    athlete_id = athlete_data.get("id")
    
    # Sprawdzanie, czy taki athlete już istnieje
    existing_athlete = Athlete.objects.filter(athlete_id=athlete_id).first()
    if existing_athlete:
        # Jeśli istnieje, możemy go aktualizować lub przekierować do innego widoku.
        return redirect('some_other_view_or_url_name')
    #w przyszłości trzeba zdefiniować nazwę tego widoku

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

def list_athletes(request):
    athletes = Athlete.objects.all()
    return render(request, 'Runnin/athlete_list.html', {'athletes': athletes})

def get_activities(athlete):
    """Pobiera aktywności sportowca z API Stravy."""
    headers = {
        'Authorization': f"Bearer {athlete.access_token}"
    }
    param = {'per_page': 200, 'page': 1}

    ACTIVITIES_URL = settings.ACTIVITIES_URL

    response = requests.get(ACTIVITIES_URL, headers=headers, params=param)
    
    if response.status_code != 200:
        print(f"Błąd podczas pobierania danych: {response.status_code} - {response.text}")
    else:
        return []

    activity_data_list = response.json() 
    print(activity_data_list) 
    # tutaj używamy json jako funkcji

    for activity_data in activity_data_list:
        get_activities_instance(activity_data, athlete)

    return activity_data


def get_activities_instance(activity_data, athlete):
    """Zapisuje pojedynczą aktywność do bazy danych."""
    # Spróbuj znaleźć aktywność na podstawie activity_id
    
    activity, created = Activity.objects.get_or_create(
        activity_id=activity_data['id']
    )
    # Aktualizuj lub ustaw wartości dla wszystkich pól
    activity = Activity()
    activity.athlete = athlete
    activity.activity_id = activity_data.get('id')
    activity.name = activity_data.get('name', '')
    activity.activity_type = activity_data.get('type', '')
    activity.start_date = activity_data.get('start_date', None)
    activity.external_id = activity_data.get('external_id', '')
    activity.upload_id = activity_data.get('upload_id', 0)
    activity.athlete_count = activity_data.get('athlete_count', 0)
    activity.resource_state = activity_data.get('resource_state', 1)  # assuming "meta" as default
    activity.photo_count = activity_data.get('photo_count', 0)
    activity.distance = activity_data.get('distance', 0.0)
    activity.moving_time = activity_data.get('moving_time', 0)
    activity.elapsed_time = activity_data.get('elapsed_time', 0)
    activity.average_speed = activity_data.get('average_speed', 0.0)
    activity.max_speed = activity_data.get('max_speed', 0.0)
    activity.average_cadence = activity_data.get('average_cadence', None)
    activity.total_elevation_gain = activity_data.get('total_elevation_gain', 0.0)
    activity.start_latlng = ','.join(map(str, activity_data.get('start_latlng', [])))  # converting list of latlng to string
    activity.end_latlng = ','.join(map(str, activity_data.get('end_latlng', [])))  # converting list of latlng to string
    activity.calories = activity_data.get('calories', 0)
    activity.has_heartrate = activity_data.get('has_heartrate', '')
    activity.achievement_count = activity_data.get('achievement_count', 0)
    activity.kudos_count = activity_data.get('kudos_count', 0)
    activity.comment_count = activity_data.get('comment_count', 0)
    activity.save()
    
    return activity, created

def activities_list(request, athlete_id):
    activities = Activity.objects.filter(athlete__athlete_id=athlete_id)
    return render(request, 'Runnin/activities_list.html', {'activities': activities})







#view creates or updates particular activity displaying all available data 
# def activity_detail(data):
#     activity_id = data.get("id")

#     # Sprawdzanie, czy taka aktywność już istnieje
#     existing_activity = Activity.objects.filter(activity_id=activity_id).first()
#     if existing_activity:
#         activity = existing_activity
#     else:
#         # Jeśli nie istnieje, tworzymy nowy obiekt Activity
#         activity = Activity()

#     # Uwzględniamy, że każda aktywność musi być powiązana z athletem.
#     athlete_data = data.get("athlete")
#     athlete_id = athlete_data.get("id")
#     athlete = Athlete.objects.get(athlete_id=athlete_id)
#     activity.athlete = athlete

#     activity.activity_id = activity_id
#     activity.name = data.get("name")
#     activity.activity_type = data.get("type")
#     activity.start_date = data.get("start_date")
#     activity.external_id = data.get("external_id")
#     activity.upload_id = data.get("upload_id")
#     activity.distance = data.get("distance")
#     activity.moving_time = data.get("moving_time")
#     activity.elapsed_time = data.get("elapsed_time")
#     activity.average_speed = data.get("average_speed")
#     activity.max_speed = data.get("max_speed")
#     activity.average_cadence = data.get("average_cadence", None)  # Uwzględnienie domyślnej wartości None
#     activity.total_elevation_gain = data.get("total_elevation_gain")
#     activity.start_latlng = ",".join(map(str, data.get("start_latlng")))  # Konwersja listy na ciąg znaków
#     activity.end_latlng = ",".join(map(str, data.get("end_latlng")))    # Konwersja listy na ciąg znaków
#     activity.calories = data.get("calories")
#     activity.has_heartrate = data.get("has_heartrate", "")
#     activity.achievement_count = data.get("achievement_count")
#     activity.kudos_count = data.get("kudos_count")
#     activity.comment_count = data.get("comment_count")
#     activity.save()

#     if existing_activity:
#         #w przyszłości trzeba zdefiniować nazwę tego widoku
#         return redirect('some_other_view_or_url_name_for_update')
#     else:
#         #w przyszłości trzeba zdefiniować nazwę tego widoku
#         return redirect('some_other_view_or_url_name_for_creation')




