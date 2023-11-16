import psycopg2
import pytest
from src.dbworker import PostgresWorker
from src.utils import create_database

name = 'test'
password = '12345'


@pytest.fixture
def create_test_database():
    # фикстура создания тестовой БД и таблиц

    conn = psycopg2.connect(password=password, user='postgres')
    conn.autocommit = True
    with conn.cursor() as cur:
        cur.execute(f"DROP DATABASE {name}")
    conn.close()

    create_database(name, password)

    db_test = PostgresWorker(name, password)
    db_test.create_table()


@pytest.fixture()
def data_for_db():
    data = {
        'problems': [
            {'contestId': 1895, 'index': 'C', 'name': 'TEST',
             'type': 'PROGRAMMING', 'tags': ['brute force', 'dp'],
             'rating': 1000},
            {'contestId': 1893, 'index': 'C', 'name': 'Freedom of Choice',
             'type': 'PROGRAMMING', 'points': 1250.0,
             'tags': ['brute force', 'implementation'], 'rating': 2000},
            {'contestId': 1893, 'index': 'A', 'name': 'Anonymous Informant',
             'type': 'PROGRAMMING', 'points': 500.0,
             'tags': ['graphs', 'implementation'], 'rating': 1500},
            ],
        'problemStatistics': [
            {'contestId': 1895, 'index': 'C', 'solvedCount': 6817},
            {'contestId': 1893, 'index': 'C', 'solvedCount': 780},
            {'contestId': 1893, 'index': 'A', 'solvedCount': 4225}]
    }
    return data


def test_get_topic(create_test_database, data_for_db):
    # TestCase1 вывод списка тем

    db = PostgresWorker(name, password)
    db.add_data(data_for_db)

    assert db.get_topic() == [('brute force',), ('dp',),
                              ('implementation',), ('graphs',)]


def test_get_max_rating(create_test_database, data_for_db):
    # TestCase2 получение максимальной сложности

    db = PostgresWorker(name, password)
    db.add_data(data_for_db)

    assert db.get_max_rating() == 2000


def test_get_min_rating(create_test_database, data_for_db):
    # TestCase3 получение минимальной сложности

    db = PostgresWorker(name, password)
    db.add_data(data_for_db)

    assert db.get_min_rating() == 1000
