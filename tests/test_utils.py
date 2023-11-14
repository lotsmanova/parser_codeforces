import psycopg2
import pytest
from src.utils import create_database, check_create_db

name = 'test'
password = '12345'


@pytest.fixture
def create_test_database():
    # фикстура создания тестовой БД

    conn = psycopg2.connect(password=password, user='postgres')
    conn.autocommit = True
    with conn.cursor() as cur:
        cur.execute(f"DROP DATABASE {name}")
    conn.close()

    create_database(name, password)


def test_check_create_db(create_test_database):
    # TestCase 1 проверка создания БД

    assert check_create_db(name, password) is True
