from datetime import datetime
import time
import os

from apscheduler.schedulers.background import BackgroundScheduler


def job():
    """Функция для запуска парсера каждый час"""

    print('Программа запущена! Время: %s' % datetime.now())


if __name__ == '__main__':
    scheduler = BackgroundScheduler()
    scheduler.add_job(job, 'interval', hours=1)
    scheduler.start()
    print('Нажмите Ctrl+{0}, чтобы завершить работу программы'.format('Break' if os.name == 'nt' else 'C'))

    try:
        while True:
            time.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
