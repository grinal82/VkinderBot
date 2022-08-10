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
import time


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


def send_photo(user_id, attachment, keyboard=None):
    # attachment = image_uploader(url)
    vk.method(
        'messages.send', {
            'user_id': user_id,
            'attachment': attachment,
            'random_id': random.randint(0, 2048)
        })


#  формирование аттачмент для отправки через send_photo
def image_uploader(url):
    result = requests.get(url).content
    img = BytesIO(result)
    image = uploader.photo_messages(img)
    media_id = str(image[0]['id'])
    owner_id = str(image[0]['owner_id'])
    attachment = f'photo{owner_id}_{media_id}'
    return attachment


load_dotenv()
# получаем созданный ранее токен группы для работы бота
token = os.getenv("VK_API_TOKEN")

# Авторизуемся как группа VK
vk = vk_api.VkApi(token=token)
uploader = vk_api.upload.VkUpload(vk)
# Работа с сообщениями
longpoll = VkLongPoll(vk)


#  Функция циклического отслеживания сообщаний
def loop_bot():
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW:
            if event.to_me:
                message_text = event.text
                return message_text, event.user_id


login = os.getenv("LOGIN")
password = os.getenv("PASSWORD")
db_name = os.getenv("DB_NAME")

DSN = f"postgresql://{login}:{password}@localhost:5432/{db_name}"

engine = sqlalchemy.create_engine(DSN)
DBsession = sessionmaker(bind=engine)
session = DBsession

print("Server started")

if __name__ == '__main__':
    while True:
        text, user_id = loop_bot()
        print(f'New message from {user_id}', end='')
        bot = VkBot(user_id, session)
        create_tables(engine)
        keyboard = VkKeyboard()
        keyboard.add_button("Поехали!", VkKeyboardColor.PRIMARY)
        write_msg(user_id, bot.new_message(text))
        if text.lower() == 'да' or text.lower() == "поехали!":
            write_msg(user_id, "Лови подборку кандидатов", keyboard)
            result = bot.search_all(user_id)
            # bot.create_json(result)
            for i in range(len(result)):
                pers_photo = bot.get_photo(result[i][0])
                if pers_photo == 'доступ к фото ограничен':
                    continue
                sorted_pers_photo = bot.sort_photos(pers_photo)
                write_msg(user_id,
                          f'\n{result[i][1]}{result[i][2]}\n{result[i][3]}')
                try:
                    send_photo(user_id,
                               attachment=','.join([
                                   sorted_pers_photo[-1][1],
                                   sorted_pers_photo[-2][1],
                                   sorted_pers_photo[-3][1]
                               ]))
                except IndexError:
                    for photo in range(len(sorted_pers_photo)):
                        send_photo(user_id,
                                   attachment=sorted_pers_photo[photo][1])
                        try:
                            add_info(
                                f'{result[i][1]}{result[i][2]}',
                                f'{result[i][3]}',
                                [
                                    sorted_pers_photo[0][1],
                                    #  sorted_pers_photo[0][0],
                                ])
                        except AttributeError:
                            write_msg(user_id, 'Произошла ошибка')
                            break
