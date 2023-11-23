import psycopg2
from src.config import db_user


class PostgresMixin:
    """Класс миксин для работы с БД"""

    @staticmethod
    def check_create_table(db_name: str, db_password: str) -> bool:
        """Метод проверки создания таблиц"""
        with psycopg2.connect(dbname=db_name, password=db_password, user=db_user) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1 FROM pg_tables WHERE tablename='topics'")
                exists = cur.fetchone()

            return exists

    @staticmethod
    def get_topic(db_name: str, db_password: str) -> tuple:
        """Метод получения списка тем"""

        with psycopg2.connect(dbname=db_name, password=db_password, user=db_user) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT topic_name FROM topics
                    """
                )

                topic_name = cur.fetchall()

            return topic_name

    @staticmethod
    def get_max_rating(db_name: str, db_password: str) -> int:
        """Метод получения максимальной сложности задач"""

        with psycopg2.connect(dbname=db_name, password=db_password, user=db_user) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                        SELECT MAX(rating) FROM tasks
                        """
                )
                max_rating = cur.fetchone()[0]

            return max_rating

    @staticmethod
    def get_min_rating(db_name: str, db_password: str) -> int:
        """Метод получения минимальной сложности задач"""

        with psycopg2.connect(dbname=db_name, password=db_password, user=db_user) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT MIN(rating) FROM tasks
                    """
                )
                min_rating = cur.fetchone()[0]

            return min_rating

    @staticmethod
    def get_data_for_user(db_name: str, db_password: str, topic: str, rating_from: int, rating_to: int) -> list:
        with psycopg2.connect(dbname=db_name, password=db_password, user=db_user) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT topic_id FROM topics
                    WHERE topic_name = %s
                    """,
                    (topic,)
                )
                topic_id = cur.fetchone()

                cur.execute(
                    f"""
                    SELECT * FROM tasks
                    WHERE rating BETWEEN {rating_from} AND {rating_to}
                    AND topic_id = {topic_id[0]}
                    ORDER BY solved_count DESC
                    LIMIT 10;
                    """
                )

                tasks_codeforces = cur.fetchall()
                return tasks_codeforces
