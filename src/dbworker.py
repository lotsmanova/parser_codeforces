from abc import ABC, abstractmethod
import psycopg2
from src.config import db_user, db_host
from src.mixinpostgres import PostgresMixin


class DBWorker(ABC):
    """Абстрактный класс для работы с БД"""

    @abstractmethod
    def create_table(self):
        """Создание таблицы в БД"""
        pass

    @abstractmethod
    def add_data(self, data):
        """Добавление данных в БД"""
        pass


class PostgresWorker(DBWorker, PostgresMixin):

    def __init__(self, db_name: str, password: str) -> None:
        self.db_name = db_name
        self.user = db_user
        self.password = password
        self.host = db_host

    def __str__(self):
        return f'{self.db_name}'

    def __repr__(self):
        return (f'PostgresWorker(db_name={self.db_name}, '
                f'password={self.password}, user={self.user})')

    def create_table(self) -> None:
        """Создание таблицы в БД"""

        with psycopg2.connect(dbname=self.db_name, password=self.password, user=self.user, host=self.host) as conn:

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

    def get_topic_for_check(self, tag):
        """Проверка существования темы в БД"""
        with psycopg2.connect(dbname=self.db_name, password=self.password, user=self.user) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT topic_id FROM topics WHERE topic_name = %s
                    """,
                    (tag,)
                )

                topic_id = cur.fetchone()

                return topic_id

    def get_task_for_check(self, task):
        """Проверка существования задачи  в БД"""
        with psycopg2.connect(dbname=self.db_name, password=self.password, user=self.user) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT task_id FROM tasks
                    WHERE task_name = %s AND task_number = %s
                    """,
                    (task['name'], f"{task['contestId']}{task['index']}",)
                )

                task_id = cur.fetchone()

                return task_id

    def add_data(self, data_codeforces: dict) -> None:
        """Добавление данных в БД"""

        with psycopg2.connect(dbname=self.db_name, password=self.password, user=self.user) as conn:
            with conn.cursor() as cur:
                for task in data_codeforces['problems']:

                    # проверка существования записи
                    for tag in task['tags']:

                        topic_id = self.get_topic_for_check(tag)

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
                            conn.commit()

                        # проверка существования записи
                        task_id = self.get_task_for_check(task)

                        if task_id is None:
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
                            conn.commit()

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
                                conn.commit()
                                break
