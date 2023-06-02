import json
import sqlite3
from sqlite3 import Error
import strava_work as sw
import os



#ACTIVITIES_URL = "https://www.strava.com/api/v3/athlete/activities"


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
    except Error as e:
        print(e)


    # creating a database connection
    conn = create_connection('strava.db')

    if conn is not None:
        # Define SQL queries for creating tables
        sql_create_athletes_table = """CREATE TABLE IF NOT EXISTS athletes (
                                        athlete_ID INTEGER PRIMARY KEY,
                                        activity_ID INTEGER NOT NULL,
                                        athlete_profile_URL TEXT NOT NULL,
                                        FOREIGN KEY (activity_id) REFERENCES activities (activity_id)
                                    );"""

        sql_create_access_tokens_table = """CREATE TABLE IF NOT EXISTS access_tokens (
                                        athlete_id INTEGER PRIMARY KEY,
                                        access_token TEXT NOT NULL,
                                        refresh_token TEXT NOT NULL,
                                        last_refresh_date DATE NOT NULL,
                                        FOREIGN KEY (athlete_id) REFERENCES athletes (athlete_ID),
                                        FOREIGN KEY (activity_id) REFERENCES activities (activity_id)
                                    );"""

        sql_create_activities_table = """CREATE TABLE IF NOT EXISTS activities (
                                        Activity_id INTEGER PRIMARY KEY,
                                        Athlete_id INTEGER NOT NULL,
                                        Activity_type TEXT NOT NULL,
                                        Location_country TEXT NOT NULL,
                                        Activity_name TEXT NOT NULL,
                                        Start_date DATE NOT NULL,
                                        Athlete_count INTEGER NOT NULL,
                                        Distance FLOAT NOT NULL,
                                        Moving_time FLOAT NOT NULL,
                                        FLOAT INTEGER NOT NULL,
                                        AVG_speed FLOAT NOT NULL,
                                        MAX_speed FLOAT NOT NULL,
                                        Has_heartrate INTEGER NOT NULL,
                                        AVG_heartrate FLOAT,
                                        MAX_heartrate FLOAT,
                                        kudos_count INTEGER NOT NULL,
                                        comment_count INTEGER NOT NULL,

                                        AVG_watts INTEGER,
                                        Map_latline TEXT NOT NULL,
                                        FOREIGN KEY (athlete_id) REFERENCES athletes (athlete_ID)
                                        );"""

        sql_create_kudoers_table = """CREATE TABLE IF NOT EXISTS kudoers (
                                        athlete_id INTEGER,
                                        kudo TEXT,
                                        FOREIGN KEY (athlete_id) REFERENCES athletes (athlete_ID),
                                        FOREIGN KEY (activity_id) REFERENCES activities (activity_id)
                                    );"""

        sql_create_comments_table = """CREATE TABLE IF NOT EXISTS comments (
                                        athlete_id INTEGER NOT NULL,
                                        activity_id INTEGER NOT NULL,
                                        comments_count TEXT,
                                        comment_1 TEXT,
                                        comment_2 TEXT,
                                        comment_3 TEXT,
                                        comment_4 TEXT,
                                        comment_5 TEXT,
                                        comment_6 TEXT,
                                        comment_7 TEXT,
                                        comment_8 TEXT,
                                        comment_9 TEXT,
                                        comment_10 TEXT,
                                        FOREIGN KEY (athlete_id) REFERENCES athletes (athlete_ID),
                                        FOREIGN KEY (activity_id) REFERENCES activities (activity_id)
                                    );"""

        # Create tables
        cur(create_table(conn, sql_create_athletes_table))
        cur(create_table(conn, sql_create_access_tokens_table))
        cur(create_table(conn, sql_create_activities_table))
        cur(create_table(conn, sql_create_kudoers_table))
        cur(create_table(conn, sql_create_comments_table))

        # Insert data into tables based on API response - commit changes and close connection
        access_token, activities = sw.get_activities(access_token)
        # TODO: Implement inserting data into tables based on the activities retrieved from the API

        
        conn.commit()
        conn.close()

    else:
        print("Error! Cannot create the database connection.")



def display_tables(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()

    for table in tables:
        print(table[0])

    conn.close()

def main():
    authorization_code = str(input('please submit authorization code from URL'))
    # refresh_token, access_token = get_refresh_token(authorization_code, payload)

    # creating a database connection
    conn = create_connection('strava.db')

    if conn is not None:


        # Insert data into tables based on API response - commit changes and close connection
        access_token, activities = sw.get_activities(authorization_code)
        # TODO: Implement inserting data into tables based on the activities retrieved from the API

        conn.commit()

        # Display tables
        display_tables(conn)

        conn.close()
    else:
        print("Error! Cannot create the database connection.")

if __name__ == '__main__':
    main()


