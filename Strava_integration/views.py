from django.shortcuts import render, redirect, get_object_or_404
import requests
from Strava_integration.models import Athlete, Activity, Comment, Kudoers
from django.conf import settings
from django.http import JsonResponse, Http404, HttpResponseServerError, HttpResponseNotFound
from django.utils import timezone


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
        print(response.json())

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

def strava_success(request):

    return render(request, 'Runnin/strava_success.html')


def strava_error(request):

    return render(request, 'Runnin/strava_error.html')


def initiate_strava_auth(request):
    strava_auth_url = (
        "https://www.strava.com/oauth/authorize"
        "?client_id={client_id}"
        "&redirect_uri={redirect_uri}"
        "&response_type=code"
        "&approval_prompt=auto"  
        "&scope=activity:read_all,activity:write"
    ).format(
        client_id=settings.STRAVA_CLIENT_ID,
        redirect_uri="http://127.0.0.1:8000/Runnin/strava_callback/" 
    )

    return redirect(strava_auth_url)

def strava_callback(request):
    auth_code = request.GET.get('code')

    if auth_code:
        response = requests.post(
            settings.AUTH_URL,
            data={
                'client_id': settings.STRAVA_CLIENT_ID,
                'client_secret': settings.STRAVA_CLIENT_SECRET,
                'code': auth_code,
                'grant_type': 'authorization_code'
            }
        )

        if response.status_code == 200:
            data = response.json()
            athlete_data = data.get("athlete")
            if athlete_data is None:
                return redirect('strava_error')

            athlete_id = athlete_data.get("id")
            existing_athlete = Athlete.objects.filter(athlete_id=athlete_id).first()

            if existing_athlete:
                # Aktualizacja istniejącego obiektu Athlete
                existing_athlete.refresh_token = data.get("refresh_token")
                existing_athlete.access_token = data.get("access_token")
                existing_athlete.expires_at = data.get("expires_at")
                existing_athlete.save()
            else:
                # Tworzenie nowego obiektu Athlete
                Athlete.objects.create(
                    athlete_id=athlete_id,
                    refresh_token=data.get("refresh_token"),
                    access_token=data.get("access_token"),
                    expires_at=data.get("expires_at"),
                    firstname=athlete_data.get("firstname"),
                    lastname=athlete_data.get("lastname"),
                    city=athlete_data.get("city"),
                    state=athlete_data.get("state"),
                    country=athlete_data.get("country"),
                    sex=athlete_data.get("sex"),
                    follower_count=athlete_data.get("follower_count"),
                    following_count=athlete_data.get("following_count")
                )

            return redirect('strava_success')
        else:
            return redirect('strava_error')
    else:
        return redirect('trava_error')

def create_athlete_instance(data):
    athlete_data = data.get("athlete")
    if athlete_data is None:
        return print("No athlete data")
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
    athlete.follower_count = athlete_data.get("follower_count")
    athlete.following_count = athlete_data.get("following_count")
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
    ACTIVITIES_URL = settings.ACTIVITIES_URL
    all_activities = []

    # Iteracja przez strony od 1 do 10
    for page in range(1, 20):
        param = {'per_page': 200, 'page': page}
        response = requests.get(ACTIVITIES_URL, headers=headers, params=param)

        if response.status_code != 200:
            # Kontynuacja w przypadku błędu na jednej ze stron
            continue

        try:
            activity_data_list = response.json()
            all_activities.extend(activity_data_list)
        except ValueError:  # obejmuje simplejson.decoder.JSONDecodeError
            # Obsługa błędu dekodowania JSON, kontynuacja pętli
            continue

    for activity_data in all_activities:
        get_activities_instance(activity_data, athlete)

    return render(request, 'Runnin/activities_list.html', {'activity_data_list': all_activities})
    

def get_activities_instance(activity_data, athlete):
    """Zapisuje pojedynczą aktywność do bazy danych."""

    defaults = {
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
    }

    activity, created = Activity.objects.get_or_create(activity_id=activity_data['id'], defaults=defaults)

    # Update only if the object already existed
    if not created:
        for key, value in defaults.items():
            setattr(activity, key, value)
        activity.save()

    return activity, created

def update_activities(request):
    athletes = Athlete.objects.all()
    for athlete in athletes:
        get_activities(request, athlete.id)
    
    
    return JsonResponse({"message": "Activities updated for all athletes"})



def activities_list(request, athlete_id):
    athlete = get_object_or_404(Athlete, pk=athlete_id)
    activity_data_list = Activity.objects.filter(athlete=athlete).order_by('-start_date')

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

def activity_comments(request, activity_id):

    try:
        activity = Activity.objects.get(id=activity_id)
        athlete = activity.athlete  
    except Activity.DoesNotExist:
        raise Http404(f"Activity with ID {activity_id} does not exist.")
    
    if not is_token_valid(athlete):
        refreshed = refresh_access_token(athlete)
        if not refreshed:
            raise ValueError("Failed to refresh access token")

    # Ustal prawidłowy URL do komentarzy
    COMMENTS_URL_TEMPLATE = "https://www.strava.com/api/v3/activities/{}/comments"
    comments_url = COMMENTS_URL_TEMPLATE.format(activity.activity_id)

    headers = {"Authorization": f"Bearer {athlete.access_token}"}
    response = requests.get(comments_url, headers=headers)
    
    if response.status_code != 200:
        print(f"Fetching comments from: {comments_url}")
        raise Exception(f"Error fetching data from Strava: {response.status_code} - {response.text}")

    comments_data = response.json()

    Comment.objects.filter(activity_id=activity_id, athlete=athlete).delete()
    for comment_data in comments_data:
        c_firstname = comment_data.get('athlete').get('firstname')
        c_lastname = comment_data.get('athlete').get('lastname')
        text = comment_data.get('text')
        Comment.objects.create(
            athlete=athlete,
            activity_id=activity_id,
            text=f"{c_firstname} {c_lastname}, comment: {text}",
            created_at=comment_data['created_at']
        )
    
    stored_comments = Comment.objects.filter(activity_id=activity_id, athlete=athlete)
    context = {
    'comments': stored_comments,
    'activity_id': activity_id,
    'athlete_id': athlete.id,
    }

    return render(request, 'Runnin/activity_comments.html', context)


def activity_kudos(request, activity_id):
    try:
        activity = Activity.objects.get(id=activity_id)
        athlete = activity.athlete  
    except Activity.DoesNotExist:
        raise Http404(f"Activity with ID {activity_id} does not exist.")
    
    if not is_token_valid(athlete):
        refreshed = refresh_access_token(athlete)
        if not refreshed:
            raise ValueError("Failed to refresh access token")

    # Ustal prawidłowy URL do komentarzy
    KUDOERS_URL_TEMPLATE = "https://www.strava.com/api/v3/activities/{}/kudos"
    kudoers_url = KUDOERS_URL_TEMPLATE.format(activity.activity_id)

    headers = {"Authorization": f"Bearer {athlete.access_token}"}
    response = requests.get(kudoers_url, headers=headers)
    
    if response.status_code != 200:
        print(f"Fetching comments from: {kudoers_url}")
        raise Exception(f"Error fetching data from Strava: {response.status_code} - {response.text}")
    
    kudoers_data = response.json()

    Kudoers.objects.filter(activity_id=activity_id, athlete=athlete).delete()
    for kudoer_data in kudoers_data:
        c_firstname = kudoer_data.get('firstname')
        c_lastname = kudoer_data.get('lastname')
        Kudoers.objects.create(
            athlete=athlete,
            activity_id=activity_id,
            kudoer =f"{c_firstname} {c_lastname}",
        )
    
    stored_kudos = Kudoers.objects.filter(activity_id=activity_id, athlete=athlete)
    context = {
    'kudoer': stored_kudos,
    'activity_id': activity_id,
    'athlete_id': athlete.id,
    }

    return render(request, 'Runnin/kudos_list.html', context)
