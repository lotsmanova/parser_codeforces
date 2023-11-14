import psycopg2
import telebot
from src.dbworker import PostgresWorker
from src.main import token_tg, db_name, db_password

bot = telebot.TeleBot(token_tg)

topic = ''
rating = 0

db_worker = PostgresWorker(db_name, db_password)

min_rating = db_worker.get_min_rating()
max_rating = db_worker.get_max_rating()

list_topic_db = db_worker.get_topic()


@bot.message_handler(content_types=['text'])
def start(message):
    """Функция привествия пользователя"""

    if message.text == '/start':
        bot.send_message(
            message.from_user.id,
            "Привет! Я бот для получения задач с сайта codeforces.com."
            "Чтобы получить задачи с сайта, следуй дальнейшим инструкциям."
            f"Выбери уровень сложности от {min_rating} до {max_rating}"
        )
    else:
        bot.send_message(
            message.from_user.id,
            "Напиши '/start'"
        )

    bot.register_next_step_handler(message, get_rating)


def get_rating(message):
    """Функция выбора сложности задачи"""

    global rating
    rating = message.text
    list_str_topic = []

    for tuple_topic in list_topic_db:
        str_topic = ''.join(tuple_topic)
        list_str_topic.append(str_topic)
    list_topic = '\n'.join(list_str_topic)

    bot.send_message(message.from_user.id, f'Выбери одну из тем: \n'
                                           f'{list_topic}')

    bot.register_next_step_handler(message, get_topic)


def get_topic(message):
    """Функция выбора темы"""

    global topic
    topic = message.text.lower()
    bot.send_message(message.from_user.id, f'Обрабатываю запрос на получение задач по теме "{topic}" со сложностью {rating}')
    bot.register_next_step_handler(message, get_data_db)

@bot.message_handler(func=lambda message: True)
def get_data_db(message):
    """Функция получения данных из БД"""

    global rating
    global topic
    conn = psycopg2.connect(dbname=db_name, password=db_password, user='postgres')
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT topic_id FROM topics 
            WHERE topic_name = %s
            """,
            (topic,)
        )
        topic_id = cur.fetchone()

        if topic_id is None:
            bot.send_message(message.from_user.id, f'Тема "{topic}" не найдена в базе данных')

        cur.execute(
            f"""
            SELECT * FROM tasks
            WHERE rating = %s AND topic_id = {topic_id[0]}
            LIMIT 10;
            """,
            (rating,)
        )

        tasks_codeforces = cur.fetchall()

        if tasks_codeforces is None:
            bot.send_message(message.from_user.id, f'Задач по вашему запросу не найдено')

        else:
            tasks_str = []
            i = 0
            for task in tasks_codeforces:
                i += 1
                task_num = task[2]
                task_name = task[1]
                count = task[4]
                tasks_str.append(f"{i}. Номер задачи: {task_num}, название: {task_name}, количество решений: {count}")

            bot.send_message(message.from_user.id, f'Задачи по вашему запросу: \n' + '\n'.join(tasks_str))
            bot.send_message(message.from_user.id, 'Ваш запрос выполнен, чтобы отправить новый запрос, введите: "/start"')


bot.polling(none_stop=True, interval=0)
