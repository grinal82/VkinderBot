import bs4 as bs4
import requests
from dotenv import load_dotenv
import os
from pprint import pprint
import datetime
import vk_api
import json
import time

load_dotenv()

td = datetime.datetime.now().date()
# получаем групповой
token = os.getenv("VK_API_TOKEN")

# получаем созданный ранее персональный токен
pers_token = os.getenv("PersonalToken")

vk = vk_api.VkApi(token=token)
version = '5.131'

NUMBER_OF_PHOTOS = 3
HOST = r'https://api.vk.com'


class VkBot:

    def __init__(self, user_id, db_session):
        print("\nСоздан объект бота!")

        self._USER_ID = user_id
        self._USERNAME = self._user_name_from_vk_id(user_id)

        self._COMMANDS = ["ПРИВЕТ", "САЛЮТ", "ХАЙ", "ЗДОРОВА"]
        self._COMMANDS2 = "ПОЕХАЛИ!"

    def _user_name_from_vk_id(self, user_id):
        request = requests.get("https://vk.com/id" + str(user_id))
        bs = bs4.BeautifulSoup(request.text, "html.parser")

        user_name = self._clean_all_tag_from_str(bs.findAll("title")[0])

        return user_name.split()[0]

    def new_message(self, message):

        # Привет
        if message.upper() in self._COMMANDS:
            return f"Категорически приветствую, {self._USERNAME}!\nХочешь найти вторую половинку?"
        elif message.upper() == self._COMMANDS2:
            return f"{self._USERNAME}, продолжим? \U0001F609"
        else:
            return "О чём это ты..."

    @staticmethod
    def _clean_all_tag_from_str(string_line):
        """
        Очистка строки stringLine от тэгов и их содержимых
        param string_line: Очищаемая строка
        return: очищенная строка
        """

        result = ""
        not_skip = True
        for i in list(string_line):
            if not_skip:
                if i == "<":
                    not_skip = False
                else:
                    result += i
            else:
                if i == ">":
                    not_skip = True

        return result

    def info_on_city(self, user_id):

        info = vk.method('users.get', {
            'user_id': user_id,
            'fields': 'city',
        })
        city = info[0]['city']['title']
        print(f'Пользователь из города: {city}')
        return city

    def info_on_sex(self, user_id):

        info = vk.method('users.get', {
            'user_id': user_id,
            'fields': 'sex',
        })
        sex = info[0]['sex']
        print(f'Половая принадлежность пользователя: {sex}')
        return sex

    def info_on_age(self, user_id):

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
        return age_years

    def search_all(self, user_id):
        user_city = self.info_on_city(user_id)
        user_sex = self.info_on_sex(user_id)
        user_age_to = self.info_on_age(user_id)
        user_age_from = user_age_to - 10
        # user_id_list = []
        if user_sex == 2:
            user_sex -= 1
        elif user_sex == 1:
            user_sex += 1
        json_to_save = []
        offset = 10
        count = 10
        params = {
            'access_token': pers_token,
            'v': version,
            'sex': user_sex,  # пол пользователя
            'hometown': user_city,  # город пользователя
            'age_from': user_age_from,  # Возраст пользователя, от
            'age_to': user_age_to,  # Возраст пользователя, до
            'sort':
            1,  # Cортировка результатов по популярности. Будем предлагать для знакомства сначала самых популярных пользователей.
            'offset': offset,
            'fields': {'domain', 'photo_max'},
            'has_photo': 1,  # Ищем только пользователей с фотографией
            'status': {
                1, 5, 6
            },  # Ищем только пользователей со статусом "не женат (не замужем)", "всё сложно",  "в активном поиске"
            # Исключаем тех, чей статус:  "встречается", "помолвлен(-а)", "женат (замужем)", "влюблен(-а)", "в гражданском браке"
            'count': count
        }
        url = f'{HOST}/method/users.search'
        response = requests.get(url, params=params).json()
        time.sleep(0.3)
        offset += count
        per_info = response['response']['items']
        for info in per_info:
            data_on_user = {}
            data_on_user['id'] = info['id']
            data_on_user['first_name'] = info['first_name']
            data_on_user['last_name'] = info['last_name']
            data_on_user['account_type'] = info['is_closed']
            json_to_save.append(data_on_user)
            pprint(json_to_save)
            with open('data.json', 'w') as write_file:
                json.dump(json_to_save, write_file, indent=4)

    @staticmethod
    def get_photo():
        with open('data.json') as f:
            data = json.load(f)
            for i in data:
                VK_USER_ID = i.get('id')
                first_name = i.get('first_name')
                last_name = i.get('last_name')
                account_type = i.get('account_type')
                params = {
                    'owner_id': VK_USER_ID,
                    'access_token': pers_token,
                    'v': '5.131',
                    'album_id': 'profile',
                    'extended': '1',
                    'photo_sizes': '1',
                    'count': NUMBER_OF_PHOTOS
                }
                url = f'{HOST}/method/photos.get'
                if account_type == False:
                    response = requests.get(url, params).json()
                    time.sleep(0.3)
                    items = response['response']['items']
                    # print(response)
                    for x in items:
                        for k, v in x.items():
                            if k == 'sizes':
                                x['sizes'] = v[-1]

                    for x in items[
                            -3:]:  # Выводим ссылки последних 3 фотографий с наибольшим количеством лайков

                        url = (x['sizes']['url'])
                        return url
