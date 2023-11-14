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
            {'contestId': 1895, 'index': 'C', 'name': 'TEST', 'type': 'PROGRAMMING', 'tags': ['brute force', 'dp', 'hashing', 'implementation', 'math']},
            {'contestId': 1893, 'index': 'C', 'name': 'Freedom of Choice', 'type': 'PROGRAMMING', 'points': 1250.0, 'tags': ['brute force', 'implementation']},
            {'contestId': 1893, 'index': 'A', 'name': 'Anonymous Informant', 'type': 'PROGRAMMING', 'points': 500.0, 'tags': ['graphs', 'implementation']},
            ],
        'problemStatistics': [
            {'contestId': 1895, 'index': 'C', 'solvedCount': 6817},
            {'contestId': 1893, 'index': 'C', 'solvedCount': 780},
            {'contestId': 1893, 'index': 'A', 'solvedCount': 4225}]
    }
    return data


def test_check_create_table(create_test_database):
    # TestCase1 проверка создания таблиц

    db_test = PostgresWorker(name, password)
    assert db_test.check_create_table() is True


def test_add_data(create_test_database, data_for_db):
    # TestCase2 проверка заполнения БД

    db_test = PostgresWorker(name, password)
    db_test.add_data(data_for_db)

    with db_test.conn.cursor() as cur:
        for task in data_for_db['problems']:
            cur.execute(
                """
                SELECT task_name, task_number FROM tasks WHERE task_name = %s AND task_number = %s
                """,
                (task['name'], f"{task['contestId']}{task['index']}",)
            )
            result1 = cur.fetchone()

            cur.execute(
                """
                SELECT task_name FROM tasks WHERE task_name = %s
                """,
                ("TEST",)
            )
            result2 = cur.fetchone()[0]

            assert result1 is not None, f"Задача {task['name']} не найдена в базе данных"
            assert result2 == 'TEST'
