class PostgresMixin:
    """Класс миксин для работы с БД"""

    def check_create_db(self):
        """Метод проверки создания БД"""
        with self.conn.cursor() as cur:
            cur.execute(f"SELECT 1 FROM pg_database WHERE datname='{self.db_name}'")
            exists = cur.fetchone()
            if exists:
                return True
            else:
                return False

    def check_create_table(self):
        """Метод проверки создания таблиц"""

        with self.conn.cursor() as cur:
            cur.execute(f"SELECT 1 FROM pg_tables WHERE tablename='topics' AND tablename='tasks'")
            exists = cur.fetchone()
            if exists:
                return True
            else:
                return False

    def get_topic(self) -> list:
        """Метод получения списка тем"""

        with self.conn.cursor() as cur:
            cur.execute(
                """
                SELECT topic_name FROM topics
                """
            )

            topic_name = cur.fetchall()

        return topic_name

    def get_max_rating(self) -> int:
        """Метод получения максимальной и минимальной сложности задач"""

        with self.conn.cursor() as cur:
            cur.execute(
                """
                SELECT MAX(rating) FROM tasks
                """
            )
            max_rating = cur.fetchone()[0]

            cur.execute(
                """
                SELECT MIN(rating) FROM tasks
                """
            )
            min_rating = cur.fetchone()[0]

        return max_rating, min_rating

    def get_data_to_param(self, rating: str, topic: str) -> list:
        """Метод получения задач по переданным параметрам"""

        with self.conn.cursor() as cur:
            cur.execute(
                """
                SELECT * FROM tasks 
                WHERE rating = %s AND
                topic_id = (SELECT topic_id FROM topics WHERE topic_name = %s)
                LIMIT 10;
                """,
                (rating, topic,)
            )

            tasks_codeforces = cur.fetchall()
        return tasks_codeforces