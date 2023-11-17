from abc import ABC, abstractmethod
import psycopg2
from src.mixinpostgres import PostgresMixin


class DBWorker(ABC):
    """Абстрактный класс для работы с БД"""

    @abstractmethod
    def create_table(self):
        pass

    @abstractmethod
    def add_data(self, data):
        pass

    @abstractmethod
    def end_connect(self):
        pass


class PostgresWorker(DBWorker, PostgresMixin):

    def __init__(self, db_name: str, password: str, user='postgres') -> None:
        self.db_name = db_name
        self.user = user
        self.password = password
        self.conn = psycopg2.connect(dbname=self.db_name,
                                     password=self.password, user=self.user)

    def __str__(self):
        return f'{self.db_name}'

    def __repr__(self):
        return (f'PostgresWorker(db_name={self.db_name}, '
                f'password={self.password}, user={self.user})')

    def create_table(self) -> None:
        """Создание таблицы в БД"""

        with self.conn.cursor() as cur:
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

        self.conn.commit()

    def add_data(self, data_codeforces: dict) -> None:
        """Добавление данных в БД"""

        with self.conn.cursor() as cur:
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

                    # проверка существования записи
                    cur.execute(
                        """
                        SELECT task_name, task_number FROM tasks
                        WHERE task_name = %s AND task_number = %s
                        """,
                        (task['name'], f"{task['contestId']}{task['index']}",)
                    )

                    task_id = cur.fetchone()

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
            self.conn.commit()

    def end_connect(self) -> None:
        """Метод для завершения подключения к БД"""

        self.conn.close()
