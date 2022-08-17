import random
import os
from dotenv import load_dotenv
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from VKbot import VkBot
import sqlalchemy
from sqlalchemy.orm import sessionmaker
from Database.logic_db import create_tables, add_user, add_info, add_photo, check_favorite, check_db_master, check_candidate
from io import BytesIO
import requests
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
    """
    Функция отправки сообщений в чат
    Принимает id текущего юзера и аттачмент в фомате 'photo{owner_id}_{media_id}'
    """

    vk.method(
        'messages.send', {
            'user_id': user_id,
            'attachment': attachment,
            'random_id': random.randint(0, 2048)
        })


#  формирование аттачмент для отправки через send_photo --- использовалась для проверки
def image_uploader(url):
    """
    Вспомогательная функция для получения attachment нужного для отправки фото 
    """
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


# Получаем доступ к БД
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

        keyboard = VkKeyboard(one_time=True)
        keyboard.add_button("Поехали!", VkKeyboardColor.PRIMARY)
        write_msg(
            user_id, f"Вас приветствует бот - VkinderBot\n"
            f"\nХочешь найти вторую половинку?\n 1 - Начать поиск    2 - Избранное"
        )
        if text.lower() == 'да' or text.lower() == "поехали!" or text == '1':
            bot = VkBot(user_id)
            create_tables(engine)
            add_user(user_id)
            write_msg(user_id, "Лови подборку кандидатов", keyboard)
            result = bot.search_all(
                user_id)  # Ищем кандидатов (100 человек) -> список списков
            bot.create_json(result)
            current_user_id = check_db_master(user_id)
            for i in range(len(result)):
                selected_user = check_candidate(result[i][0])
                pers_photo = bot.get_photo(result[i][0])
                time.sleep(0.2)
                if pers_photo == 'доступ к фото ограничен' or selected_user is not None:
                    continue
                sorted_pers_photo = bot.sort_photos(pers_photo)
                write_msg(user_id,
                          f'\n{result[i][1]} {result[i][2]}\n{result[i][3]}'
                          )  #Выводим в чат данные по и-той анкете
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
                        # Предлагаем пользователю либо добавить анкету в избранное, либо двигаться дальше
                write_msg(user_id, '1 - Добавить, 2 - Далее, 3 - выйти')
                text, user_id = loop_bot()
                if text == '1':
                    if i >= len(result) - 1:
                        write_msg(
                            user_id,
                            "Это была последняя анкета,\nнажмите 2 для просмотра избранного"
                        )
                        break
                    try:
                        #Если пользователь ввел "1" добавляем в БД вызвав add_info и затем add_photo
                        add_info(vk_id=f'{int(result[i][0])}',
                                 first_name=f'{result[i][1]}',
                                 last_name=f'{result[i][2]}',
                                 link=f'{result[i][3]}',
                                 id_user=current_user_id.id)
                        selected_user = check_candidate(
                            id=f'{int(result[i][0])}')
                        add_photo(photo=sorted_pers_photo[0][1],
                                  photo_id=selected_user.id)
                    except AttributeError:
                        write_msg(user_id, 'Произошла ошибка')
                        break
                elif text == '2':
                    if i >= len(result) - 1:
                        write_msg(
                            user_id,
                            "Это была последняя анкета,\nнажмите 2 для просмотра избранного"
                        )
                        break
                elif text == '3':
                    write_msg(user_id,
                              f'Введите - 2  чтобы посмотреть избранное')
                    break
        elif text == '2':
            result = check_favorite(user_id)
            for nums, users in enumerate(result):
                write_msg(
                    user_id,
                    f'{users.first_name}, {users.last_name}, {users.link}')
