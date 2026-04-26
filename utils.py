import psycopg2
from config import config

def create_database():
    """Создает базу данных и таблицы."""
    params = config()
    conn = psycopg2.connect(**params)
    conn.autocommit = True
    cur = conn.cursor()
    cur.execute(f"DROP DATABASE IF EXISTS hh_vacancies")
    cur.execute(f"CREATE DATABASE hh_vacancies")
    cur.close()
    conn.close()

    params['database'] = 'hh_vacancies'
    conn = psycopg2.connect(**params)
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE employers (
            employer_id INTEGER PRIMARY KEY,
            employer_name VARCHAR(255) NOT NULL,
            employer_url VARCHAR(255)
        );
    """)
    cur.execute("""
        CREATE TABLE vacancies (
            vacancy_id INTEGER PRIMARY KEY,
            employer_id INTEGER REFERENCES employers(employer_id),
            vacancy_name VARCHAR(255) NOT NULL,
            salary_from INTEGER,
            salary_to INTEGER,
            vacancy_url VARCHAR(255)
        );
    """)
    conn.commit()
    cur.close()
    conn.close()
