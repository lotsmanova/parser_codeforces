class PostgresMixin:
    """Класс миксин для работы с БД"""

    def check_create_table(self):
        """Метод проверки создания таблиц"""

        with self.conn.cursor() as cur:
            cur.execute("SELECT 1 FROM pg_tables WHERE tablename='topics'")
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
        """Метод получения максимальной сложности задач"""

        with self.conn.cursor() as cur:
            cur.execute(
                """
                SELECT MAX(rating) FROM tasks
                """
            )
            max_rating = cur.fetchone()[0]

        return max_rating

    def get_min_rating(self) -> int:
        """Метод получения минимальной сложности задач"""

        with self.conn.cursor() as cur:
            cur.execute(
                """
                SELECT MIN(rating) FROM tasks
                """
            )
            min_rating = cur.fetchone()[0]

        return min_rating
