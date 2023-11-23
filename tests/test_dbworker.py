import psycopg2
from src.config import db_name, db_password, db_user
from tests.conftests import db_worker, data_for_test, get_bd_connection, db_create_table

test_db_name = db_name + '_test'


def test_add_data(get_bd_connection, db_create_table, db_worker, data_for_test):

    db_test = db_worker
    db_test.add_data(data_for_test)

    with psycopg2.connect(dbname=test_db_name, password=db_password, user=db_user) as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT task_name FROM tasks
                """
            )
            task_name = cur.fetchone()

            # TestCase2 проверка заполнения БД
            assert task_name[0] == data_for_test['problems'][0]['name']
