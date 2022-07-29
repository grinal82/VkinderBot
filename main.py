import random
import os
from dotenv import load_dotenv
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from VKbot import VkBot


def write_msg(user_id, message):
    """
    Функция write_msg получает id пользователя ВК <user_id>, 
    которому оно отправит сообщение и собственно само сообщение
    """
    vk.method(
        'messages.send', {
            'user_id': user_id,
            'message': message,
            'random_id': random.randint(0, 2048)
        })


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
