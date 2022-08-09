import unittest
from logic_db import create_tables, engine, get_all_info, add_info, delete_info, get_name_with_id


class TestFunctions(unittest.TestCase):

    def test_create_database(self):
        result = create_tables(engine)
        etalon = 'New database was created!'
        self.assertEqual(result, etalon)

    # Started this test only if test_delete_info is commented
    def test_get_all_info(self):
        name = 'Danil Dzuba'
        url = 'htsdoijfdds/dasokjdsia'
        photos = ['dsadasdsa', 'sdadasdsadas']
        add_info(name, url, photos)
        result = get_all_info(1)
        etalon = {'name': 'Danil Dzuba', 'url': 'htsdoijfdds/dasokjdsia', 'photos': "['dsadasdsa', 'sdadasdsadas']"}
        self.assertEqual(result, etalon)

    def test_delete_info(self):
        name = 'Danil Dzuba'
        url = 'htsdoijfdds/dasokjdsia'
        photos = ['dsadasdsa', 'sdadasdsadas']
        add_info(name, url, photos)
        result = delete_info(1)
        etalon = f'Пользователь {name} успешно удален из избранных'
        self.assertEqual(result, etalon)

    # Started this test only if test_delete_info is commented
    def test_get_name_with_id(self):
        name = 'Danil Dzuba'
        url = 'htsdoijfdds/dasokjdsia'
        photos = ['dsadasdsa', 'sdadasdsadas']
        add_info(name, url, photos)
        result = get_name_with_id()
        etalon = {'1': 'Danil Dzuba'}
        self.assertEqual(result, etalon)

