import psycopg2
import pytest
from config_for_test import db_user, db_name, db_host, db_password
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
             'tags': ['brute force', 'implementation'], 'rating': 1000},
            {'contestId': 3, 'index': 'C', 'name': 'test3', 'type': 'PROGRAMMING', 'points': 500.0,
             'tags': ['graphs', 'implementation'], 'rating': 10},
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
        cur.execute(
            f"SELECT pg_terminate_backend(pg_stat_activity.pid) "
            f"FROM pg_stat_activity "
            f"WHERE pg_stat_activity.datname = '{test_db_name}' AND pid <> pg_backend_pid();")
        cur.execute(f"DROP DATABASE {test_db_name}")
    conn.close()


@pytest.fixture(scope='function')
def get_bd_connection():
    create_test_database()
    yield
    remote_test_database()


@pytest.fixture(scope='function')
def db_worker():
    return PostgresWorker(test_db_name, main_db_creds['password'])


@pytest.fixture(scope='function')
def db_create_table(db_worker):
    worker = db_worker
    worker.create_table()


@pytest.fixture(scope='function')
def data_for_test():
    return get_data_test()
