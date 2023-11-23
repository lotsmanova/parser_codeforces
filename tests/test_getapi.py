from src.getapi import CodeforcesAPI


def test_success_get_data():

    api = CodeforcesAPI('https://codeforces.com/api/problemset.problems')

    result = api.get_data()
    # TestCase1 проверка получения данных по API
    assert 'problems' in result


def test_failed_get_data():
    # TestCase 1 проверка получения данных по API

    api = CodeforcesAPI('https://codeforces.com/api/test')

    result = api.get_data()
    # TestCase2 проверка получения данных по API
    assert result == 'Ошибка при получении данных'
