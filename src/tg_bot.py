import re

import psycopg2
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from src.dbworker import PostgresWorker
from src.main import token_tg, db_name, db_password

bot = telebot.TeleBot(token_tg)

db_worker = PostgresWorker(db_name, db_password)

min_rating = db_worker.get_min_rating()
max_rating = db_worker.get_max_rating()

# default values
topic = ''
rating = min_rating
running = True

list_topic_db = db_worker.get_topic()
list_str_topic = []

for tuple_topic in list_topic_db:
    str_topic = ''.join(tuple_topic)
    list_str_topic.append(str_topic)


@bot.message_handler(content_types=['text'])
def start(message):
    """Функция привествия пользователя"""

    global running
    if message.text == '/start':
        running = True
        bot.send_message(
            message.from_user.id,
            "Привет! Я бот для получения задач с сайта codeforces.com"
            "Чтобы получить задачи с сайта, следуй дальнейшим инструкциям.\nЧтобы остановить бота, введите '/stop'"
        )
        bot.send_message(
            message.from_user.id,
            f"Выбери уровень сложности от {min_rating} до {max_rating}"
        )
        bot.register_next_step_handler(message, get_rating)

    elif message.text == '/stop':
        stop(message)

    else:
        bot.send_message(
            message.from_user.id,
            "Чтобы отправить запрос, введите '/start'"
        )


@bot.message_handler(commands=['stop'])
def stop(message):
    global running
    running = False

    bot.send_message(message.from_user.id, "Бот остановлен")


def get_rating(message):
    """Функция выбора сложности задачи"""

    global rating

    if message.text != '/stop':

        if message.text.isdigit():
            if min_rating <= int(message.text) <= max_rating:
                rating = message.text

                main_kb = InlineKeyboardMarkup()
                buttons = []
                for topic_task in list_str_topic:
                    buttons.append(InlineKeyboardButton(topic_task, callback_data=topic_task))

                main_kb.add(*buttons)

                bot.send_message(message.from_user.id, 'Выбери одну из тем: \n', reply_markup=main_kb)

            else:
                bot.send_message(
                    message.from_user.id,
                    f"Сложность должна быть в диапазоне от {min_rating} до {max_rating}. Повторите запрос"
                )
                start(message)

        else:
            bot.send_message(
                message.from_user.id,
                "Сложность должна быть числом. Повторите запрос"
            )
            start(message)
    else:
        stop(message)


@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    global topic
    if not running:
        return
    topic = call.data
    for topic_task in list_str_topic:
        if topic_task in call.data:
            bot.send_message(call.message.chat.id,
                             f'Обрабатываю запрос на получение задач по теме "{topic}" со сложностью {rating}')
            bot.send_message(call.message.chat.id,
                             f'Чтобы получить ответ на запрос, введите "ok"')
            bot.register_next_step_handler(call.message, get_data_db)


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
            start(message)

        cur.execute(
            f"""
            SELECT * FROM tasks
            WHERE rating = %s AND topic_id = {topic_id[0]}
            ORDER BY solved_count DESC
            LIMIT 10;
            """,
            (rating,)
        )

        tasks_codeforces = cur.fetchall()

        if tasks_codeforces != []:

            tasks_str = []
            i = 0
            for task in tasks_codeforces:
                i += 1
                task_num = task[2]
                task_name = task[1]
                count = task[4]

                slice_num = task_num[-2:]
                if slice_num[0].isalpha():
                    num_for_link = task_num[:len(task_num) - 2]
                    index = slice_num
                else:
                    num_for_link = task_num[:len(task_num) - 1]
                    index = task_num[-1:]

                task_link = f"https://codeforces.com/problemset/problem/{num_for_link}/{index}"
                task_text = (f"{i}. Номер задачи: {task_num};\nНазвание: {task_name};\nКоличество решений: {count};\n"
                             f"<a href='{task_link}'>Ссылка на задачу</a>\n")
                tasks_str.append(task_text)

            tasks_message = "Задачи по вашему запросу:\n\n" + "\n".join(tasks_str)
            bot.send_message(message.from_user.id, tasks_message, parse_mode="HTML")
            bot.send_message(message.from_user.id, f'Чтобы отправить новый запрос, введите "/start"')

        else:
            bot.send_message(message.from_user.id, 'Задач по вашему запросу не найдено. Повторите запрос')
            start(message)


while running:
    bot.polling(none_stop=True, interval=0)
