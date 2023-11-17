import os
from src.getapi import CodeforcesAPI
from src.dbworker import PostgresWorker
from dotenv import load_dotenv
from src.utils import create_database, check_create_db

load_dotenv('../.env')

db_name = os.getenv('DB_NAME')
db_password = os.getenv('DB_PASSWORD')
token_tg = os.getenv('TELEGRAM_TOKEN')
api_codeforces = os.getenv('API_CODEFORCES')


def main():
    codeforces_api = CodeforcesAPI(api_codeforces)

    # parser data in codeforces
    codeforces_data = codeforces_api.get_data()
    print('Получены данные с сайта codeforces.com')

    # create db
    if check_create_db is False:
        create_database(db_name, db_password)
        print(f'Создана база данных {db_name}')
    else:
        print(f"База данных {db_name} уже существует")

    # create table
    db_worker = PostgresWorker(db_name, db_password)

    if db_worker.check_create_table() is False:
        db_worker.create_table()
        print('Созданы таблицы topics и tasks')
    else:
        print("Таблицы topics и tasks уже существуют")

    # add data to db
    db_worker.add_data(codeforces_data)
    print(f'Добавлены данные в БД {db_name}')

    db_worker.end_connect()


if __name__ == '__main__':
    main()
