import psycopg2
from psycopg2 import sql
import os

# DATABASE = "postgresql://username:password@localhost:5432/readmedatabase"

DB_USER = os.getenv('DB_USER', 'postgres')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'password')
DB_HOST = os.getenv('DB_HOST', 'db')
DB_PORT = os.getenv('DB_PORT', '5432')
DB_NAME = os.getenv('DB_NAME', 'readmedatabase')

DATABASE = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"


def init_db():
    try:
        conn = psycopg2.connect(DATABASE)
        cur = conn.cursor()

        # Create tables
        cur.execute('''
        CREATE TABLE IF NOT EXISTS projects (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            status TEXT
        );
        ''')

        cur.execute('''
        CREATE TABLE IF NOT EXISTS datasets (
            id SERIAL PRIMARY KEY,
            project_id INTEGER NOT NULL,
            name TEXT,
            FOREIGN KEY (project_id) REFERENCES projects(id)
        );
        ''')

        cur.execute('''
        CREATE TABLE IF NOT EXISTS datasets_metadata (
            id SERIAL PRIMARY KEY,
            dataset_id INTEGER NOT NULL,
            key TEXT NOT NULL,
            value TEXT NOT NULL,
            FOREIGN KEY (dataset_id) REFERENCES datasets(id)
        );
        ''')

        cur.execute('''
        CREATE TABLE IF NOT EXISTS patients (
            id SERIAL PRIMARY KEY,
            project_id INTEGER NOT NULL,
            ext_patient_id TEXT,
            ext_patient_url TEXT,
            public_patient_id TEXT,
            FOREIGN KEY (project_id) REFERENCES projects(id)
        );
        ''')

        cur.execute('''
        CREATE TABLE IF NOT EXISTS patients_metadata (
            id SERIAL PRIMARY KEY,
            patient_id INTEGER NOT NULL,
            key TEXT,
            value TEXT,
            FOREIGN KEY (patient_id) REFERENCES patients(id)
        );
        ''')

        cur.execute('''
        CREATE TABLE IF NOT EXISTS samples (
            id SERIAL PRIMARY KEY,
            patient_id INTEGER NOT NULL,
            ext_sample_id TEXT,
            ext_sample_url TEXT,
            FOREIGN KEY (patient_id) REFERENCES patients(id)
        );
        ''')

        cur.execute('''
        CREATE TABLE IF NOT EXISTS samples_metadata (
            id SERIAL PRIMARY KEY,
            sample_id INTEGER NOT NULL,
            key TEXT,
            value TEXT,
            FOREIGN KEY (sample_id) REFERENCES samples(id)
        );
        ''')

        cur.execute('''
        CREATE TABLE IF NOT EXISTS raw_files (
            id SERIAL PRIMARY KEY,
            dataset_id INTEGER NOT NULL,
            path TEXT,
            FOREIGN KEY (dataset_id) REFERENCES datasets(id)
        );
        ''')

        cur.execute('''
        CREATE TABLE IF NOT EXISTS raw_files_metadata (
            metadata_id SERIAL PRIMARY KEY,
            raw_file_id INTEGER,
            metadata_key TEXT NOT NULL,
            metadata_value TEXT NOT NULL,
            FOREIGN KEY (raw_file_id) REFERENCES raw_files (id)
        );
        ''')

        conn.commit()

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if 'conn' in locals():
            conn.close()
