import psycopg2
from src.utils import create_database, check_create_db
from config import db_name, db_password, db_user
from tests.conftests import get_bd_connection

test_db_name = db_name + '_test'
password = db_password


def test_create_db():
    create_database(test_db_name, password)

    # TestCase 1 создание БД
    assert True

    conn = psycopg2.connect(password=password, user=db_user)
    conn.autocommit = True
    with conn.cursor() as cur:
        cur.execute(f"DROP DATABASE {test_db_name}")

    conn.close()


def test_check_create_db(get_bd_connection):

    # TestCase 2 проверка создания БД
    assert check_create_db(test_db_name, db_password) is not None
