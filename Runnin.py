import subprocess
import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import json
import sqlite3
from sqlite3 import Error
import pandas as pd

#run the 1st script
subprocess.run(['python.py', 'strava_work.py'], shell = True)


#run 2nd script and get the output
subprocess.run(['python.py', '2_Database_work.py'], capture_output= True, text = True, shell = True)

#conversion to a dataframe
df = pd.Dataframe(activities)
print(df)
