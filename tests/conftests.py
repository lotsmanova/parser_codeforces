import psycopg2
import pytest
from src.config import db_user, db_name, db_host, db_password
from src.dbworker import PostgresWorker

main_db_creds = {
    'host': db_host,
    'name': db_name,
    'password': db_password,
    'user': db_user
}

test_db_name = main_db_creds['name'] + '_test'


def create_test_database():

    conn = psycopg2.connect(password=main_db_creds['password'], user=main_db_creds['user'])
    conn.autocommit = True
    with conn.cursor() as cur:
        cur.execute(f"CREATE DATABASE {test_db_name}")

    conn.close()


def get_data_test():
    data = {
        'problems': [
            {'contestId': 1, 'index': 'A', 'name': 'test1', 'type': 'PROGRAMMING',
             'tags': ['brute force', 'dp', 'hashing', 'implementation', 'math']},
            {'contestId': 2, 'index': 'B', 'name': 'test2', 'type': 'PROGRAMMING', 'points': 1250.0,
             'tags': ['brute force', 'implementation']},
            {'contestId': 3, 'index': 'C', 'name': 'test3', 'type': 'PROGRAMMING', 'points': 500.0,
             'tags': ['graphs', 'implementation']},
            ],
        'problemStatistics': [
            {'contestId': 1, 'index': 'A', 'solvedCount': 6817},
            {'contestId': 2, 'index': 'B', 'solvedCount': 780},
            {'contestId': 3, 'index': 'C', 'solvedCount': 4225}]
    }
    return data


def remote_test_database():
    conn = psycopg2.connect(password=main_db_creds['password'], user=main_db_creds['user'])
    conn.autocommit = True
    with conn.cursor() as cur:
        cur.execute(f"DROP DATABASE {test_db_name}")

    conn.close()


@pytest.fixture(scope='session')
def get_bd_connection():
    create_test_database()
    print('create')
    yield
    remote_test_database()


@pytest.fixture(scope='session')
def db_worker():
    return PostgresWorker(test_db_name, main_db_creds['password'])


@pytest.fixture(scope='session')
def db_create_table(db_worker):
    worker = db_worker
    worker.create_table()


@pytest.fixture(scope='session')
def data_for_test():
    return get_data_test()
