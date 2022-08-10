from xml import dom
import bs4 as bs4
import requests
from dotenv import load_dotenv
import os
from pprint import pprint
import datetime
import vk_api
from vk_api import ApiError
import json
import time

load_dotenv()

td = datetime.datetime.now().date()
"""получаем групповой"""
token = os.getenv("VK_API_TOKEN")
"""получаем созданный ранее персональный токен"""
pers_token = os.getenv("PersonalToken")

vk = vk_api.VkApi(token=token)
version = '5.131'

NUMBER_OF_PHOTOS = 3
HOST = r'https://api.vk.com'


class VkBot:
    """Класс ВКбота, используется для получения от пользователей сообщений и передачи им информации
    Атрибуты:
    USER_ID - id  пользователя Вконтакте, отправившему боту сообщение
    USERNAME - имя данного пользователя
    COMMANDS - команды команды, которые бот ожидпет получить от пользователя
    COMMANDS2 - команда, после которой юзеру предоставляется информация

    Методы:
    _user_name_from_vk_id - получает id пользователя
    new_message - проверяет сообщения от пользователя
    clean_all_tag_from_str - очищает строку
    info_on_city - получение города пользователя
    info_on_sex - получение пола пользователя
    nfo_on_age - получение возраста пользователя
    search_all - поиск необходимой информации по критериям
    """

    def __init__(self, user_id, db_session):
        print("\nСоздан объект бота!")

        self._USER_ID = user_id
        self._USERNAME = self._user_name_from_vk_id(user_id)

        self._COMMANDS = ["ПРИВЕТ", "САЛЮТ", "ХАЙ", "ЗДОРОВА"]
        self._COMMANDS2 = "ПОЕХАЛИ!"

    def _user_name_from_vk_id(self, user_id):
        """Метод получения id написавшего пользователя
        Параметр - id пользователя в ВК
        Тип: Int"""
        request = requests.get("https://vk.com/id" + str(user_id))
        bs = bs4.BeautifulSoup(request.text, "html.parser")

        user_name = self._clean_all_tag_from_str(bs.findAll("title")[0])

        return user_name.split()[0]

    def new_message(self, message):
        """Метод, который проверяет полученное сообщение от пользователя
        на соответствие необходимых понятных для бота приветсвий.
        Параметр - сообщение от пользователя
        Тип - str"""
        if message.upper() in self._COMMANDS:
            return f"Категорически приветствую, {self._USERNAME}!\nХочешь найти вторую половинку?"
        elif message.upper() == self._COMMANDS2:
            return f"{self._USERNAME}, продолжим? \U0001F609"
        else:
            return "О чём это ты..."

    @staticmethod
    def _clean_all_tag_from_str(string_line):
        """ Метод очистки строки stringLine от тэгов и их содержимых
        Параметр - string_line: Очищаемая строка
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
        """Метод получения информации о городе пользователя
        Параметр - id пользователя в ВК
        Тип: Int"""
        info = vk.method('users.get', {
            'user_id': user_id,
            'fields': 'city',
        })
        city = info[0]['city']['title']
        print(f'Пользователь из города: {city}')
        return city

    def info_on_sex(self, user_id):
        """Метод получения информации о половой принадлежности пользователя
        Параметр - id пользователя в ВК
        Тип: Int"""
        info = vk.method('users.get', {
            'user_id': user_id,
            'fields': 'sex',
        })
        sex = info[0]['sex']
        print(f'Половая принадлежность пользователя: {sex}')
        return sex

    def info_on_age(self, user_id):
        """Метод получения информации о возрасте пользователя
        Параметр - id пользователя в ВК
        Тип: Int"""
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
        """Метод поиска людей исходя из заданных критериев
        Параметр - id пользователя в ВК
        Тип: Int"""
        user_city = self.info_on_city(user_id)
        user_sex = self.info_on_sex(user_id)
        user_age_to = self.info_on_age(user_id)
        user_age_from = user_age_to - 10
        if user_sex == 2:
            user_sex -= 1
        elif user_sex == 1:
            user_sex += 1
        persons = []
        offset = 0
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
            'fields': 'domain',
            'has_photo': 1,  # Ищем только пользователей с фотографией
            'status': {
                1, 5, 6
            },  # Ищем только пользователей со статусом "не женат (не замужем)", "всё сложно",  "в активном поиске"
            # Исключаем тех, чей статус:  "встречается", "помолвлен(-а)", "женат (замужем)", "влюблен(-а)", "в гражданском браке"
            'count': count
        }
        url = f'{HOST}/method/users.search'
        response = requests.get(url, params=params).json()
        time.sleep(0.2)
        offset += 1
        profile_url = 'https://vk.com/id'
        for element in response['response']['items']:
            person = [
                element['id'], element['first_name'], element['last_name'],
                profile_url + str(element['id'])
            ]
            persons.append(person)
        return persons

    def get_photo(self, id):
        params2 = {
            'owner_id': id,
            'access_token': pers_token,
            'v': '5.131',
            'album_id': 'profile',
            'extended': '1',
            'photo_sizes': '1',
            'count': NUMBER_OF_PHOTOS
        }
        url = f'{HOST}/method/photos.get'

        try:
            response = requests.get(url, params2).json()
            time.sleep(0.2)
        except ApiError:
            return 'доступ к фото ограничен'
        photos = []
        for i in range(NUMBER_OF_PHOTOS):
            try:
                photos.append([
                    response['response']['items'][i]['likes']['count'],
                    'photo' +
                    str(response['response']['items'][i]['owner_id']) + '_' +
                    str(response['response']['items'][i]['id'])
                ])
            except IndexError:
                photos.append(['нет фото'])
        return photos

    def sort_photos(self, photos):
        result = []
        for element in photos:
            if element != ['нет фото'] and photos != 'доступ к фото ограничен':
                result.append(element)
        return sorted(result)

    def create_json(List):
        json_to_save = []
        pers_info = {}
        for i, info in enumerate(data):
            pers_info['id'] = info[0]
            pers_info['first_name'] = info[1]
            pers_info['last_name'] = info[2]
            pers_info['id_link'] = info[3]
            json_to_save.append(pers_info.copy())
        with open('data.json', 'w') as write_file:
            json.dump(json_to_save, write_file, indent=4)
        return json_to_save
