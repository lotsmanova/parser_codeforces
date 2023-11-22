import psycopg2


def create_database(db_name, password, user='postgres') -> None:
    """Создание БД"""

    conn = psycopg2.connect(password=password, user=user)
    conn.autocommit = True
    with conn.cursor() as cur:
        cur.execute(f"CREATE DATABASE {db_name}")

    conn.close()


def check_create_db(db_name, password, user):
    """Метод проверки создания БД"""
    conn = psycopg2.connect(password=password, user=user)
    with conn.cursor() as cur:
        cur.execute(f"SELECT 1 FROM pg_database WHERE datname='{db_name}'")
        exists = cur.fetchone()
        return exists
