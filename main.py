import random
import os
from dotenv import load_dotenv
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from VKbot import VkBot
import datetime

td = datetime.datetime.now().date()


def write_msg(user_id, message):
    """
    Функция write_msg получает id пользователя ВК <user_id>, 
    которому оно отправит сообщение и собственно само сообщение
    random_id - уникальный идентификатор, 
    предназначенный для предотвращения повторной отправки одинакового сообщения. 
    """
    vk.method(
        'messages.send', {
            'user_id': user_id,
            'message': message,
            'random_id': random.randint(0, 2048)
        })


def info_on_city(user_id):

    info = vk.method('users.get', {
        'user_id': user_id,
        'fields': 'city',
    })
    city = info[0]['city']['title']
    print(f'Пользователь из города: {city}')


def info_on_sex(user_id):

    info = vk.method('users.get', {
        'user_id': user_id,
        'fields': 'sex',
    })
    sex = info[0]['sex']
    print(f'Половая принадлежность пользователя: {sex}')


def info_on_age(user_id):

    info = vk.method('users.get', {
        'user_id': user_id,
        'fields': 'bdate',
    })
    bdate = info[0]['bdate']
    print(f'Пользователь родился: {bdate}')
    year = int(bdate.split(".")[2])
    month = int(bdate.split(".")[1])
    day = int(bdate.split(".")[0])
    bd = datetime.date(year, month, day)
    age_years = int((td - bd).days / 365.25)
    print(f'Пользователю {age_years} лет')


def search_friends():
    users = vk.method('users.search', {
        'sort': '0',
        'city': 'Тула',
        'sex': '0'
    })
    print(users).json()


load_dotenv()
# получаем созданный ранее токен
token = os.getenv("VK_API_TOKEN")

# Авторизуемся как группа VK
vk = vk_api.VkApi(token=token)

# Работа с сообщениями
longpoll = VkLongPoll(vk)

print("Server started")
for event in longpoll.listen():

    if event.type == VkEventType.MESSAGE_NEW:

        if event.to_me:

            print(f'New message from {event.user_id}', end='')

            bot = VkBot(event.user_id)

            write_msg(event.user_id, bot.new_message(event.text))
            info_on_city(event.user_id)
            info_on_sex(event.user_id)
            info_on_age(event.user_id)
            search_friends()
