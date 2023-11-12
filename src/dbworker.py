import os
from abc import ABC, abstractmethod

import psycopg2
from dotenv import load_dotenv

load_dotenv('../.env')

db_name = os.getenv('DB_NAME')
db_password = os.getenv('DB_PASSWORD')


class DBWorker(ABC):
    """Абстрактный класс для работы с БД"""

    @abstractmethod
    def create_database(self):
        pass

    @abstractmethod
    def create_table(self):
        pass

    @abstractmethod
    def add_data(self, data):
        pass


class PostgresWorker(DBWorker):

    def __init__(self, db_name: str, password: str, user='postgres') -> None:
        self.db_name = db_name
        self.user = user
        self.password = password


    def __str__(self):

        return f'{self.db_name}'


    def __repr__(self):

        return f'PostgresWorker(db_name={self.db_name}, password={self.password}, user={self.user})'

    def create_database(self) -> None:
        """Создание БД"""

        conn = psycopg2.connect(password=self.password, user=self.user)
        conn.autocommit = True
        with conn.cursor() as cur:
            cur.execute(f"CREATE DATABASE {self.db_name}")

        conn.close()

    def create_table(self) -> None:
        """Создание таблицы в БД"""

        conn = psycopg2.connect(dbname=db_name, password=self.password, user=self.user)
        with conn.cursor() as cur:
            cur.execute("""
                    CREATE TABLE topics 
                    (
                        topic_id serial PRIMARY KEY,
                        topic_name varchar(255) NOT NULL
                    );
                """)

            cur.execute("""
                    CREATE TABLE tasks 
                    (
                        task_id serial PRIMARY KEY,
                        task_name varchar(255) NOT NULL,
                        task_number varchar(100) NOT NULL,
                        topic_id int REFERENCES topics(topic_id),
                        solved_count int,
                        rating int
                    );
                """)

        conn.commit()
        conn.close()

    def add_data(self, data_codeforces: list[dict]) -> None:
        conn = psycopg2.connect(dbname=db_name, password=self.password, user=self.user)
        with conn.cursor() as cur:
            for task in data_codeforces['problems']:
                # проверка существования записи
                for tag in task['tags']:
                    cur.execute(
                        """
                        SELECT topic_id FROM topics WHERE topic_name = %s
                        """,
                        (tag,)
                    )

                    topic_id = cur.fetchone()

                    if topic_id is None:
                        # Если topic нет в таблице, добавляем новый id
                        cur.execute(
                            """
                            INSERT INTO topics (topic_name)
                            VALUES (%s)
                            RETURNING topic_id
                            """,
                            (tag,)
                        )
                        topic_id = cur.fetchone()[0]


                    # добавляем данные в таблицу tasks
                    cur.execute(
                        """
                        INSERT INTO tasks (topic_id, task_name, task_number, rating)
                        VALUES (%s, %s, %s, %s)
                        RETURNING task_id
                        """,
                        (topic_id, task['name'], f"{task['contestId']}{task['index']}", task.get('rating'))
                    )
                    task_id = cur.fetchone()[0]

                    for count in data_codeforces['problemStatistics']:
                        if f"{count['contestId']}{count['index']}" == f"{task['contestId']}{task['index']}":
                            cur.execute(
                                """
                                UPDATE tasks
                                SET solved_count = %s
                                WHERE task_id = %s
                                """,
                                (count['solvedCount'], task_id)
                            )
                            break

            # завершение сеанса подключения
            conn.commit()
            conn.close()



test = PostgresWorker(db_name, db_password)
data = {'problems':
    [
        {'contestId': 1895, 'index': 'C', 'name': 'Torn Lucky Ticket', 'type': 'PROGRAMMING',
         'tags': ['brute force', 'dp', 'hashing', 'implementation', 'math']},
        {'contestId': 1893, 'index': 'C', 'name': 'Freedom of Choice', 'type': 'PROGRAMMING', 'points': 1250.0,
         'tags': ['brute force', 'implementation']},
        {'contestId': 1893, 'index': 'A', 'name': 'Anonymous Informant', 'type': 'PROGRAMMING', 'points': 500.0,
         'tags': ['graphs', 'implementation']},
        {'contestId': 1891, 'index': 'E', 'name': 'Brukhovich and Exams', 'type': 'PROGRAMMING', 'points': 2000.0,
         'tags': ['brute force', 'greedy', 'implementation', 'math', 'sortings']},
        {'contestId': 1890, 'index': 'B', 'name': 'Qingshan Loves Strings', 'type': 'PROGRAMMING', 'points': 750.0,
         'tags': ['constructive algorithms', 'implementation']},
        {'contestId': 1889, 'index': 'D', 'name': 'Game of Stacks', 'type': 'PROGRAMMING', 'points': 2000.0,
         'tags': ['brute force', 'dfs and similar', 'graphs', 'implementation', 'trees']},
        {'contestId': 1889, 'index': 'A', 'name': 'Qingshan Loves Strings 2', 'type': 'PROGRAMMING', 'points': 750.0,
         'tags': ['constructive algorithms', 'greedy', 'implementation']}
    ],
    'problemStatistics':
        [
            {'contestId': 1895, 'index': 'C', 'solvedCount': 6817},
            {'contestId': 1893, 'index': 'C', 'solvedCount': 780},
            {'contestId': 1893, 'index': 'A', 'solvedCount': 4225},
            {'contestId': 1891, 'index': 'E', 'solvedCount': 487},
            {'contestId': 1890, 'index': 'B', 'solvedCount': 13807},
            {'contestId': 1889, 'index': 'D', 'solvedCount': 317},
            {'contestId': 1889, 'index': 'A', 'solvedCount': 9092}
        ]
}
# test.create_database()
# test.create_table()
test.add_data(data)