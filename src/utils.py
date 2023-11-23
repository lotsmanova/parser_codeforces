import psycopg2
from src.config import db_user


def create_database(db_name, password) -> None:
    """Создание БД"""

    conn = psycopg2.connect(password=password, user=db_user)
    conn.autocommit = True
    with conn.cursor() as cur:
        cur.execute(f"CREATE DATABASE {db_name}")

    conn.close()


def check_create_db(db_name, password):
    """Метод проверки создания БД"""
    conn = psycopg2.connect(password=password, user=db_user)
    with conn.cursor() as cur:
        cur.execute(f"SELECT 1 FROM pg_database WHERE datname='{db_name}'")
        exists = cur.fetchone()
        return exists
