import telebot
from src.main import token_tg

bot = telebot.TeleBot(token_tg)


@bot.message_handler(content_types=['text'])
def start(message, min_rating, max_rating):
    if message.text == '/start':
        bot.send_message(
            message.from_user.id,
            "Привет! Я бот для получения задач с сайта codeforces.com. "
            "Чтобы получить задачи с сайта, следуй дальнейшим инструкциям. "
            f"Выбери уровень сложности от {min_rating} до {max_rating}"
        )
    else:
        bot.send_message(
            message.from_user.id,
            "Напиши '/start'"
        )


def get_rating(message, list_topic):
    rating = message.text
    bot.send_message(message.from_user.id, f'Выбери одну тему. '
                                           f'В списке представлены всё темы. {list_topic}')

    bot.register_next_step_handler(message, get_topic)
    return rating


def get_topic(message):
    topic = message.text
    bot.send_message(message.from_user.id, f'10 задач на выбранную тему и сложность: ')
    bot.register_next_step_handler(message, get_data_db)
    return topic


def get_data_db(message, data):
    if data:
        bot.send_message(message.from_user.id, f'{data}')
    else:
        bot.send_message(message.from_user.id, 'Таких задач нет в моей базе. '
                                               'Повторите запрос с другими параметрами. Напиши "/start"')
