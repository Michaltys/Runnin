import json
import sqlite3
from sqlite3 import Error
from CollectionProcess import get_refresh_token
import os
import csv

payload = {
    'client_id': '106874',
    'client_secret': '085ccc8a42148640c782812dc57e60e5851c5516',
    'code': 'authorization_code',
    'grant_type': 'authorization_code',
    'f': 'json'
}

ACTIVITIES_URL = "https://www.strava.com/api/v3/athlete/activities"


def create_connection(db_file):
    conn = sqlite3.connect(db_file)
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)

    return conn


def create_table(conn, create_table_sql):
    try:
        cur = conn.cursor()
        cur.execute(create_table_sql)
        print("Table created successfully")
    except Error as e:
        print(e)

def create_athletes_table(conn):
    sql_create_athletes_table = """CREATE TABLE IF NOT EXISTS athletes (
                                    athlete_ID INTEGER PRIMARY KEY,
                                    username TEXT,
                                    firstname TEXT,
                                    lastname TEXT,
                                    access_token TEXT NOT NULL,
                                    refresh_token TEXT NOT NULL,
                                    updated_at DATE NOT NULL,
                                    created_at TEXT NOT NULL
                                );"""

    # Create athletes table
    create_table(conn, sql_create_athletes_table)

def insert_athlete_data(conn, athlete_json):
    username = athlete_json.get('username') or "None"
    firstname = athlete_json.get('firstname')
    lastname = athlete_json.get('lastname')
    access_token = athlete_json.get('access_token')
    refresh_token = athlete_json.get('refresh_token')
    created_at = athlete_json.get('created_at')
    updated_at = athlete_json.get('updated_at')

    insert_athlete = "INSERT OR IGNORE INTO athletes (username, firstname, lastname, access_token, refresh_token, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?)"
    
    try:
        cur = conn.cursor()
        cur.execute(insert_athlete, (username, firstname, lastname, access_token, refresh_token, created_at, updated_at))
        conn.commit()
        print("Athlete data inserted successfully")
    except Error as e:
        print(e)



#def export_athletes_to_csv(conn, csv_file):
#
#    try:
#        cur = conn.cursor()
#        cur.execute("SELECT * FROM athletes_table")
#        rows = cur.fetchall()
#
#        with open(csv_file, 'w', newline='') as file:
#            writer = csv.writer(file)
#            writer.writerow(["athlete_ID", "username", "firstname", "lastname", "access_token", "refresh_token", "updated_at", "created_at"])
#            writer.writerows(rows)
#
#        print("Athletes exported to CSV successfully.")
#    except Error as e:
#        print(e)


def display_athletes_table(conn):
    select_athletes = "SELECT * FROM athletes"

    try:
        cur = conn.cursor()
        cur.execute(select_athletes)
        rows = cur.fetchall()

        for row in rows:
            print(row)

        print("Athletes table displayed successfully.")
    except Error as e:
        print(e)


def export_table_to_csv(conn, table_name, csv_file):
    try:
        cur = conn.cursor()
        cur.execute(f"SELECT * FROM {table_name}")
        rows = cur.fetchall()

        with open(csv_file, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([description[0] for description in cur.description])
            writer.writerows(rows)

        print("Table exported to CSV successfully.")
    except Error as e:
        print(e)


def main():
    authorization_code = str(input('Please submit the authorization code from the URL: '))
    refresh_token, access_token, athletes_json = get_refresh_token(authorization_code, payload)
    
    db_file = "athletes.db"
    conn = create_connection(db_file)

    # Create athletes table
    create_athletes_table(conn)

    conn.close()

    # Reopen connection
    conn = create_connection(db_file)

    # Extract athlete details from athletes_json
    username = athletes_json['username']
    athlete_id = athletes_json['id']
    firstname = athletes_json['firstname']
    lastname = athletes_json['lastname']
    updated_at = athletes_json['updated_at']
    created_at = athletes_json['created_at']

    # Insert athlete data into athletes table
    athlete_data = {
        'username': username,
        'athlete_id': athlete_id,
        'firstname': firstname,
        'lastname': lastname,
        'access_token': access_token,
        'refresh_token': refresh_token,
        'updated_at': updated_at,
        'created_at': created_at
    }

    insert_athlete_data(conn, athlete_data)

    conn = create_connection(db_file)  # Reopen connection

    display_athletes_table(conn)

    conn.close()

#    conn = create_connection(db_file)  # Reopen connection
#    # Export athletes to CSV
#    csv_file = "athletes.csv"
#    export_athletes_to_csv(conn, csv_file)
#    conn.close()

#   # Export athletes to CSV
#    csv_file = "athletes.db"
#    export_athletes_to_csv(csv_file, db_file)

if __name__ == '__main__':
    main()
