import random
import os
from dotenv import load_dotenv
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from VKbot import VkBot
import sqlalchemy
from sqlalchemy.orm import sessionmaker
from sqlalchemy import orm
from Database import models
from Database.logic_db import create_tables, add_info
from io import BytesIO
import requests
import json


def write_msg(user_id, message, keyboard=None):
    """
    Функция write_msg получает id пользователя ВК <user_id>, 
    которому оно отправит сообщение и собственно само сообщение
    random_id - уникальный идентификатор, 
    предназначенный для предотвращения повторной отправки одинакового сообщения. 
    """
    post = {
        'user_id': user_id,
        'message': message,
        'random_id': random.randint(0, 2048)
    }
    if keyboard != None:
        post["keyboard"] = keyboard.get_keyboard()
    else:
        post = post
    vk.method('messages.send', post)


#  функция чтобы отправлять фото
def send_photo(user_id):
    with open('data.json', 'r') as f:
        data = json.load(f)
        count = 0
        for info in data:
            while count <= len(info['photo_link']):
                photo = info['photo_link'][count]
                # count += 1

                url = "".join(photo)
                attachment = image_uploader(url)
                vk.method(
                    'messages.send', {
                        'user_id': user_id,
                        'attachment': attachment,
                        'random_id': random.randint(0, 2048)
                    })
                count += 1
            else:
                continue


def get_info_on_person():
    with open('data.json', 'r') as f:
        data = json.load(f)
        for info in data:
            name = "{} {}".format(info['last_name'], info['first_name'])
            url = info['profile_link']
            print(f'{name}\n{url}')
        return f'{name}\n{url}\n'


load_dotenv()
# получаем созданный ранее токен группы для работы бота
token = os.getenv("VK_API_TOKEN")

# Авторизуемся как группа VK
vk = vk_api.VkApi(token=token)
uploader = vk_api.upload.VkUpload(vk)


#  формирование аттачмент для отправки через send_photo
def image_uploader(url):
    result = requests.get(url).content
    img = BytesIO(result)
    image = uploader.photo_messages(img)
    media_id = str(image[0]['id'])
    owner_id = str(image[0]['owner_id'])
    attachment = f'photo{owner_id}_{media_id}'
    return attachment


# Работа с сообщениями
longpoll = VkLongPoll(vk)

login = os.getenv("LOGIN")
password = os.getenv("PASSWORD")
db_name = os.getenv("DB_NAME")

DSN = f"postgresql://{login}:{password}@localhost:5432/{db_name}"

engine = sqlalchemy.create_engine(DSN)
DBsession = orm.sessionmaker(bind=engine)

print("Server started")
with DBsession() as db_sesion:
    for event in longpoll.listen():

        if event.type == VkEventType.MESSAGE_NEW:

            if event.to_me:

                print(f'New message from {event.user_id}', end='')

                bot = VkBot(event.user_id, db_sesion)
                create_tables(engine)
                keyboard = VkKeyboard()
                keyboard.add_button("Поехали!", VkKeyboardColor.PRIMARY)
                text = event.text.lower()
                write_msg(event.user_id, bot.new_message(event.text), keyboard)

                bot.search_all(event.user_id)
                write_msg(event.user_id, get_info_on_person(), keyboard)
                send_photo(event.user_id)
                # send_photo(event.user_id)
                # send_photo(event.user_id)
