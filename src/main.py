import os
import time

from apscheduler.schedulers.background import BackgroundScheduler

from src.getapi import CodeforcesAPI
from src.dbworker import PostgresWorker
from dotenv import load_dotenv

from src.scheduler_task import job
from src.utils import create_database

load_dotenv('../.env')

db_name = os.getenv('DB_NAME')
db_password = os.getenv('DB_PASSWORD')
token_tg = os.getenv('TELEGRAM_TOKEN')


def main():
    codeforces_api = CodeforcesAPI()
    db_worker = PostgresWorker(db_name, db_password)

    # parser data in codeforces
    codeforces_data = codeforces_api.get_data()

    # create db
    if db_worker.check_create_db is False:
        create_database(db_name, db_password)

    # create table
    if db_worker.check_create_table() is False:
        db_worker.create_table()

    # add data to db
    db_worker.add_data(codeforces_data)


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





