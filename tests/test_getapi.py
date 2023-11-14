from src.getapi import CodeforcesAPI


def test_get_data():
    # TestCase 1 проверка получения данных по API

    codeforces1 = CodeforcesAPI('https://codeforces.com/api/test')
    codeforces2 = CodeforcesAPI('https://codeforces.com/api/problemset.problems')

    if 'problems' in codeforces2.get_data():
        res = True
        assert res is True
    assert codeforces1.get_data() == 'Ошибка при получении данных'
