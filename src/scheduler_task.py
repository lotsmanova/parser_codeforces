from datetime import datetime


def job():
    """Функция для запуска парсера каждый час"""

    print('Программа запущена! Время: %s' % datetime.now())
