from config import db_name, db_password
from tests.conftests import get_bd_connection, data_for_test, db_create_table, db_worker

test_db_name = db_name + '_test'
password = db_password


def test_check_create_table(get_bd_connection, db_create_table, db_worker):
    db_test = db_worker
    db_test.check_create_table(test_db_name, password)

    # TestCase1 проверка создания таблиц
    assert True


def test_get_topic(get_bd_connection, db_create_table, db_worker, data_for_test):

    db_test = db_worker
    db_test.add_data(data_for_test)

    # TestCase2 вывод списка тем
    assert db_test.get_topic(test_db_name, password) == [('brute force',), ('dp',), ('hashing',),
                                                         ('implementation',), ('math',), ('graphs',)]


def test_get_max_rating(get_bd_connection, db_create_table, db_worker, data_for_test):

    db_test = db_worker
    db_test.add_data(data_for_test)

    # TestCase3 получение максимальной сложности
    assert db_test.get_max_rating(test_db_name, password) == 1000


def test_get_min_rating(get_bd_connection, db_create_table, db_worker, data_for_test):

    db_test = db_worker
    db_test.add_data(data_for_test)

    # TestCase4 получение минимальной сложности
    assert db_test.get_min_rating(test_db_name, password) == 10


def test_get_data_for_user(get_bd_connection, db_create_table, db_worker, data_for_test):
    db_test = db_worker
    db_test.add_data(data_for_test)

    result = db_test.get_data_for_user(test_db_name, password, 'brute force', 500, 1200)

    # TestCase5 получение данных из БД по передаваемым параметрам
    assert result[0][1] == 'test2'
