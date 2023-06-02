import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import json
import pandas as pd
import datetime

AUTH_URL = "https://www.strava.com/oauth/token"
ACTIVITIES_URL = "https://www.strava.com/api/v3/athlete/activities"
ATHLETE_INFO = "https://www.strava.com/api/v3/athlete"

payload = {
    'client_id': '106874',
    'client_secret': '085ccc8a42148640c782812dc57e60e5851c5516',
    'code': 'authorization_code',
    'grant_type': 'authorization_code',
    'f': 'json'
}

def get_refresh_token(authorization_code, payload):
    payload['code'] = authorization_code
    response = requests.post(AUTH_URL, data=payload, verify=False)
#    print(response.json())
    refresh_token = response.json()["refresh_token"]
    access_token = response.json()["access_token"]

  # Get athlete information
    athlete_response = requests.get(ATHLETE_INFO, headers={'Authorization': 'Bearer ' + access_token}, verify=False)
    
    #create access_tokens df to store last access_tokens
    #access_tokens = pd.Dataframe(columns = [
    #'athlete_json', 'username', 'firstname', 'lastname','created_at' 
    #])
    
    athlete_json = athlete_response.json()
    username = athlete_json.get('username')
    firstname = athlete_json.get('firstname')
    lastname = athlete_json.get('lastname')
    created_at = athlete_json.get('created_at')
    
    print("Athelte details:")
    print("Username:", username)
    print("First Name:", firstname)
    print("Last Name:", lastname)
    print("Refresh Token:", refresh_token)
    print("Access Token:", access_token)
    print("Created At:", created_at)

    return refresh_token, access_token


def get_activities(access_token):
    header = {'Authorization': 'Bearer ' + access_token}
    param = {'per_page': 200, 'page': 1}

    activities_df = pd.DataFrame(columns=[
        'Activity ID', 'Athlete ID', 'Activity Type', 'Location Country', 'Activity Name', 'Start date',  
        'Athlete Count', 'Distance', 'Moving Time',
        'Total Elevation Gain', 'AVG Speed', 'Max Speed', 'Has Heart Rate',
        'Average Heart Rate', 'Has Kudoed', 'Kudos Count', 'Comment Count',
        'Summary Polyline'
    ])

    activities = requests.get(ACTIVITIES_URL, headers=header, params=param).json()

   #activities iteration
    for activity in activities:
        activity_id = int(activity["id"])
        athlete_id = int(activity["athlete"]["id"])
        activity_type = str(activity["sport_type"])
        location_country = str(activity["location_country"])
        activity_name = str(activity["name"])
        start_date = str(activity["start_date"])
        athlete_count = int(activity["athlete_count"])
    
        distance = int(round(activity["distance"], 2))
        moving_time = str(round(activity["moving_time"] / 60, 2))
        total_elevation_gain = int(round(activity["total_elevation_gain"], 2))
        AVG_speed = int(round(activity["average_speed"], 2))
        max_speed = int(round(activity["max_speed"], 2))
    
        has_heart_rate = activity["has_heartrate"]

        if has_heart_rate:
            avg_heart_rate = int(round(activity["average_heartrate"], 2))
        else:
            avg_heart_rate = "AVG Heart Rate not available"
        has_kudoed = activity["has_kudoed"]
        kudos_count = int(activity["kudos_count"])
        comment_count = int(activity["comment_count"])
        summary_polyline = str(activity["map"]["summary_polyline"])

        #getting data to the df

        activities_df.loc[len(activities_df)] = [
            activity_id, athlete_id, activity_type, location_country, activity_name,
            start_date, athlete_count, distance, moving_time,
            total_elevation_gain, AVG_speed, max_speed, has_heart_rate,
            avg_heart_rate, has_kudoed, kudos_count, comment_count,
            summary_polyline
        ]
    print(activities_df)
    return activities_df

if __name__ == "__main__":
    authorization_code = str(input('please submit authorization code from URL'))
    refresh_token, access_token = get_refresh_token(authorization_code, payload)
    access_token = get_activities(access_token)
