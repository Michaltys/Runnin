from django.shortcuts import render, redirect, get_object_or_404
import requests
from Strava_integration.models import Athlete, Activity, Comment
from django.conf import settings
from django.utils import timezone
from django.http import JsonResponse, Http404


#landing page
# Runnin/views.py


def landing_page(request):
    return render(request, 'Runnin/Runnin.html')


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


def is_token_valid(athlete):
    #Check if the access token is valid.
    return athlete.expires_at > timezone.now().timestamp()

def refresh_access_token(athlete):
    #Refresh the access token.
    payload = {
        'client_id': settings.STRAVA_CLIENT_ID,
        'client_secret': settings.STRAVA_CLIENT_SECRET,
        'refresh_token': athlete.refresh_token,
        'grant_type': 'refresh_token'
    }
    
    STRAVA_TOKEN_URL = settings.AUTH_URL
    
    response = requests.post(STRAVA_TOKEN_URL, data=payload, verify=True)
    
    if response.status_code == 200:
        data = response.json()
        athlete.access_token = data.get('access_token')
        athlete.refresh_token = data.get('refresh_token')
        athlete.expires_at = data.get('expires_at')
        athlete.save()
        return True
    return False

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



def get_activities(request, athlete_id):
    #gets athlete's all activities list
    try:
        athlete = Athlete.objects.get(id=athlete_id)
    except Athlete.DoesNotExist:
        raise Http404(f"Athlete with ID {athlete_id} does not exist.")
    
    if not is_token_valid(athlete):
        if not refresh_access_token(athlete):
            # Handle token refresh failure e.g. return, raise error, log etc.
            return JsonResponse({"error": "Failed to refresh access token"}, status=500)


    headers = {
        'Authorization': f"Bearer {athlete.access_token}"
    }
    param = {'per_page': 200, 'page': 1}

    ACTIVITIES_URL = settings.ACTIVITIES_URL

    response = requests.get(ACTIVITIES_URL, headers=headers, params=param)
    

    if response.status_code != 200:
        return JsonResponse({"error": f"Error fetching data: {response.status_code} - {response.text}"}, status=response.status_code)
    
    try:
        
        activity_data_list = response.json() 
        print(activity_data_list)
    except ValueError:  # includes simplejson.decoder.JSONDecodeError
        return JsonResponse({"error": "Decoding JSON has failed"}, status=500)
    
    for activity_data in activity_data_list:
        get_activities_instance(activity_data, athlete)
    return render(request, 'Runnin/activities_list.html', {'activity_data_list': activity_data_list})  # Jeśli chcesz użyć szablonu
    


def get_activities_instance(activity_data, athlete):
    """Zapisuje pojedynczą aktywność do bazy danych."""
    
    activity, created = Activity.objects.get_or_create(
        activity_id=activity_data['id'],
        defaults={
            'athlete': athlete,
            'name': activity_data.get('name', ''),
            'activity_type': activity_data.get('type', ''),
            'start_date': activity_data.get('start_date', None),
            'external_id': activity_data.get('external_id', ''),
            'upload_id': activity_data.get('upload_id', 0),
            'athlete_count': activity_data.get('athlete_count', 0),
            'resource_state': activity_data.get('resource_state', 1),
            'photo_count': activity_data.get('photo_count', 0),
            'distance': activity_data.get('distance', 0.0),
            'moving_time': activity_data.get('moving_time', 0),
            'elapsed_time': activity_data.get('elapsed_time', 0),
            'average_speed': activity_data.get('average_speed', 0.0),
            'max_speed': activity_data.get('max_speed', 0.0),
            'average_cadence': activity_data.get('average_cadence', None),
            'total_elevation_gain': activity_data.get('total_elevation_gain', 0.0),
            'start_latlng': ','.join(map(str, activity_data.get('start_latlng', []))),
            'end_latlng': ','.join(map(str, activity_data.get('end_latlng', []))),
            'calories': activity_data.get('calories', 0),
            'has_heartrate': activity_data.get('has_heartrate', False),
            'achievement_count': activity_data.get('achievement_count', 0),
            'kudos_count': activity_data.get('kudos_count', 0),
            'comment_count': activity_data.get('comment_count', 0),
            'average_temp': activity_data.get('average_temp', None),
            'average_heartrate': activity_data.get('average_heartrate', None),
            'max_heartrate': activity_data.get('max_heartrate', None),
            'pr_count': activity_data.get('pr_count', 0),
            'total_photo_count': activity_data.get('total_photo_count', 0),
            'has_kudoed': activity_data.get('has_kudoed', False)
            # Add other fields here if needed
        }
    )
    
    activity.name = activity_data.get('name', '')
    activity.activity_type = activity_data.get('type', '')
    activity.start_date = activity_data.get('start_date', None)
    activity.external_id = activity_data.get('external_id', '')
    activity.upload_id = activity_data.get('upload_id', 0)
    activity.athlete_count = activity_data.get('athlete_count', 0)
    activity.resource_state = activity_data.get('resource_state', 1)
    activity.photo_count = activity_data.get('photo_count', 0)
    activity.distance = activity_data.get('distance', 0.0)
    activity.moving_time = activity_data.get('moving_time', 0)
    activity.elapsed_time = activity_data.get('elapsed_time', 0)
    activity.average_speed = activity_data.get('average_speed', 0.0)
    activity.max_speed = activity_data.get('max_speed', 0.0)
    activity.average_cadence = activity_data.get('average_cadence', None)
    activity.total_elevation_gain = activity_data.get('total_elevation_gain', 0.0)
    activity.start_latlng = ','.join(map(str, activity_data.get('start_latlng', [])))
    activity.end_latlng = ','.join(map(str, activity_data.get('end_latlng', [])))
    activity.calories = activity_data.get('calories', 0)
    activity.has_heartrate = activity_data.get('has_heartrate', False)
    activity.achievement_count = activity_data.get('achievement_count', 0)
    activity.kudos_count = activity_data.get('kudos_count', 0)
    activity.comment_count = activity_data.get('comment_count', 0)
    activity.average_temp = activity_data.get('average_temp', None)
    activity.average_heartrate = activity_data.get('average_heartrate', None)
    activity.max_heartrate = activity_data.get('max_heartrate', None)
    activity.pr_count = activity_data.get('pr_count', 0)
    activity.total_photo_count = activity_data.get('total_photo_count', 0)
    activity.has_kudoed = activity_data.get('has_kudoed', False)

    activity.save()
    
    return activity, created


def activities_list(request, athlete_id):
    athlete = get_object_or_404(Athlete, pk=athlete_id)
    activity_data_list = Activity.objects.filter(athlete=athlete)

    # Debug
    print("Debugging Athlete:")
    print(f"ID: {athlete.id}, First Name: {athlete.firstname}, Last Name: {athlete.lastname}")

    print("Debugging Activities:")
    for activity in activity_data_list:
        print(f"Activity Name: {activity.name}, Start Date: {activity.start_date}, Athlete ID: {activity.athlete.id}, Django ID: {activity.id}")

    context = {
        'athlete': athlete,
        'activity_data_list': activity_data_list,
    }

    return render(request, 'Runnin/activities_list.html', context)


def activity_detail(request, athlete_id, activity_id):
    print(f"Athlete ID: {athlete_id}, Activity ID: {activity_id}")

    try:
        athlete = Athlete.objects.get(id=athlete_id)
        print(f"Found athlete: {athlete.firstname}")
    except Athlete.DoesNotExist:
        print(f"No athlete found with id: {athlete_id}")
        # Handle error as needed
    
    try:
        activity = Activity.objects.get(id=activity_id, athlete=athlete)
        print(f"Found activity: {activity.name}")
    except Activity.DoesNotExist:
        print(f"No activity found with id: {activity_id} for athlete {athlete.firstname}")
        # Handle error as needed
    
    context = {
        'athlete': athlete,
        'activity': activity,
    }
    return render(request, 'Runnin/activity_detail.html', context)

def activity_comments(request, athlete_id, activity_id):
    athlete = get_object_or_404(Athlete, pk=athlete_id)

    # Refresh the token if necessary
    if not refresh_access_token(athlete):
        # handle error, e.g., redirect to an error page or log the user out
        pass
    
    # Fetch comments from Strava API
    STRAVA_COMMENT_URL = f"https://www.strava.com/api/v3/activities/{activity_id}/comments"
    headers = {"Authorization": f"Bearer {athlete.access_token}"}
    response = requests.get(STRAVA_COMMENT_URL, headers=headers)
    
    comments = response.json() if response.status_code == 200 else []

    # Store comments in your database
    Comment.objects.filter(activity_id=activity_id, athlete=athlete).delete()
    for comment_data in comments:
        Comment.objects.create(
            athlete=athlete,
            activity_id=activity_id,
            text=comment_data['text'],
            created_at=comment_data['created_at'],
            # Set other fields as needed
        )
    
    # Retrieve comments from your database
    stored_comments = Comment.objects.filter(activity_id=activity_id, athlete=athlete)

    context = {
        'comments': stored_comments,
        'activity_id': activity_id,
    }
    print(context)  # or use logging

    return render(request, 'Runnin/activity_comments.html', context)