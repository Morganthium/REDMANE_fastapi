import os
import psycopg2
import csv
import argparse

# parse arguements
parser = argparse.ArgumentParser(description='Import CSV data into PostgreSQL database.')
parser.add_argument('project_id', type=int, help='The project ID to use for all records')
parser.add_argument('ext_patient_url', type=str, help='The place where this came from')
parser.add_argument('csv_file', type=str, help='The path to the CSV file to import')
args = parser.parse_args()

# get project_id and csv file name
project_id = args.project_id
ext_patient_url = args.ext_patient_url
csv_file = args.csv_file

DATABASE_CONFIG = {
    'dbname': os.getenv('DB_NAME', 'readmedatabase'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', 'password'),
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': int(os.getenv('DB_PORT', 5432))
}

conn = psycopg2.connect(**DATABASE_CONFIG)
cur = conn.cursor()

# check whether project_id exists
cur.execute('SELECT 1 FROM projects WHERE id = %s;', (project_id,))
if cur.fetchone() is None:
    cur.execute('INSERT INTO projects (id, name, status) VALUES (%s, %s, %s);',
                (project_id, f'Test Project {project_id}', 'Active'))

with open(csv_file, newline='') as csvfile:
    reader = csv.DictReader(csvfile)

    for row in reader:
        cur.execute('''
        INSERT INTO patients (project_id, ext_patient_id, ext_patient_url)
        VALUES (%s, %s, %s)
        RETURNING id;
        ''', (project_id, row['record_id'], ext_patient_url))

        patient_id = cur.fetchone()[0]

        cur.execute('''
        INSERT INTO patients_metadata (patient_id, key, value)
        VALUES (%s, %s, %s);
        ''', (patient_id, 'age_range', row['age_range']))

        cur.execute('''
        INSERT INTO patients_metadata (patient_id, key, value)
        VALUES (%s, %s, %s);
        ''', (patient_id, 'smoking', row['smoking']))

        cur.execute('''
        INSERT INTO patients_metadata (patient_id, key, value)
        VALUES (%s, %s, %s);
        ''', (patient_id, 'control', row['control']))

conn.commit()
cur.close()
conn.close()
