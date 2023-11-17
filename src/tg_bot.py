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
rating = None
running = True
rating_from = None
rating_to = None

list_topic_db = db_worker.get_topic()
list_str_topic = []

for tuple_topic in list_topic_db:
    str_topic = ''.join(tuple_topic)
    list_str_topic.append(str_topic)


@bot.message_handler(content_types=['text'])
def start(message):
    """Привествия пользователя"""

    global running
    if message.text == '/start':
        running = True
        bot.send_message(
            message.from_user.id,
            "Привет! Я бот для получения задач с сайта codeforces.com"
            "Чтобы получить задачи с сайта, следуй дальнейшим инструкциям.\n"
            "Чтобы остановить бота, введите '/stop'"
        )

        bot.send_message(
            message.from_user.id,
            "Чтобы выбрать тему, введите '/topic'"
        )
        bot.register_next_step_handler(message, get_topic)

    elif message.text == '/stop':
        stop(message)

    else:
        bot.send_message(
            message.from_user.id,
            "Чтобы отправить запрос, введите '/start'"
        )


@bot.message_handler(commands=["topic"])
def get_topic(message):
    """Выбор темы"""

    if message.text == '/topic':

        main_kb = InlineKeyboardMarkup()
        buttons_topic = []
        for topic_task in list_str_topic:
            buttons_topic.append(InlineKeyboardButton(topic_task,
                                                      callback_data=topic_task))

        main_kb.add(*buttons_topic)

        bot.send_message(message.from_user.id, 'Выберите одну из тем: \n', reply_markup=main_kb)
    else:
        bot.send_message(message.from_user.id, 'Неправильная команда. Повторите запрос')
        start(message)


@bot.callback_query_handler(func=lambda call: call.data in list_str_topic)
def callback(call):
    """Обработка темы"""

    global topic

    topic = call.data
    bot.send_message(
        call.message.chat.id,
        "Чтобы выбрать сложность, введите '/rating'"
    )

    bot.register_next_step_handler(call.message, get_rating)

    remove_inline_keyboard(call.message)


@bot.message_handler(commands=["rating"])
def get_rating(message):
    """Выбор сложности"""

    if message.text == '/rating':

        keyboard = InlineKeyboardMarkup()

        buttons_rating = []
        easy_rating = InlineKeyboardButton(text=f'Легкий уровень: {min_rating} - 1600', callback_data='rating_easy')
        buttons_rating.append(easy_rating)

        average_rating = InlineKeyboardButton(text='Средний уровень: 1600 - 2400', callback_data='rating_average')
        buttons_rating.append(average_rating)

        hard_rating = InlineKeyboardButton(text=f'Сложный уровень: 2400 - {max_rating}', callback_data='rating_hard')
        buttons_rating.append(hard_rating)

        keyboard.add(*buttons_rating)

        bot.send_message(message.from_user.id, 'Выбери уровень сложности: \n', reply_markup=keyboard)
    else:
        bot.send_message(message.from_user.id, 'Неправильная команда. Повторите запрос')
        start(message)


@bot.callback_query_handler(func=lambda call: call.data.startswith('rating_'))
def callback_rating(call):
    """Обработка сложности"""

    global rating
    global rating_from
    global rating_to

    rating = call.data

    if rating == 'rating_easy':
        rating_from = min_rating
        rating_to = 1600
    elif rating == 'rating_average':
        rating_from = 1600
        rating_to = 2400
    elif rating == 'rating_hard':
        rating_from = 2400
        rating_to = max_rating

    bot.send_message(call.message.chat.id,
                     f'Обрабатываю запрос на получение задач по теме "{topic}" '
                     f'со сложностью {rating_from} - {rating_to}')
    bot.send_message(call.message.chat.id,
                     'Чтобы получить ответ на запрос, введите "/result"')

    bot.register_next_step_handler(call.message, get_data_db)
    remove_inline_keyboard(call.message)


@bot.message_handler(commands=["result"])
def get_data_db(message):
    """Получение данных из БД"""

    if message.text == '/result':

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
                    task_text = (f"{i}. Номер задачи: {task_num};\nНазвание: {task_name};\n"
                                 f"Количество решений: {count};\n"
                                 f"<a href='{task_link}'>Ссылка на задачу</a>\n")
                    tasks_str.append(task_text)

                tasks_message = (f"Задачи по теме '{topic}' "
                                 f"со сложностью {rating_from} - {rating_to}:\n\n") + "\n".join(tasks_str)
                bot.send_message(message.from_user.id, tasks_message, parse_mode="HTML")
                bot.send_message(message.from_user.id, 'Чтобы отправить новый запрос, введите "/start"')

            else:
                bot.send_message(message.from_user.id, 'Задач по вашему запросу не найдено. Повторите запрос')
                start(message)
    else:
        bot.send_message(message.from_user.id, 'Неправильная команда. Повторите запрос')
        start(message)


def remove_inline_keyboard(message):
    """Удаление внутренней клавиатуры"""

    bot.edit_message_reply_markup(message.chat.id, message.message_id)


@bot.message_handler(commands=['stop'])
def stop(message):
    """Остановка бота"""

    global running
    running = False

    bot.send_message(message.from_user.id, "Бот остановлен")


while running:
    bot.polling(none_stop=True, interval=0)
