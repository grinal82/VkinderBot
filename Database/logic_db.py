import os

import sqlalchemy
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from Database.models import Base, Name, Photo, Url

load_dotenv('.env_example')
login = os.getenv("LOGIN")
password = os.getenv("PASSWORD")
db_name = os.getenv("DB_NAME")

DSN = f"postgresql://{login}:{password}@localhost:5432/{db_name}"
engine = sqlalchemy.create_engine(DSN)


# function for start create table
def create_tables(engine):
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)


# add info in database
def add_info(name, url, photos=None):
    Session = sessionmaker(bind=engine)
    session = Session()

    name_ = Name(name=name)
    session.add(name_)
    session.commit()

    if photos != None:
        for photo in photos:
            photo_ = Photo(photo=photo, relation=name_)
            session.add(photo_)
            session.commit()

    url_ = Url(url=url, relation=name_)
    session.add(url_)
    session.commit()

    session.close()


def get_name(num):
    Session = sessionmaker(bind=engine)
    session = Session()

    # get name
    for c in session.query(Name).filter(Name.id == num).all():
        return c
    session.close()


# Получение адреса в вк по id пользователя
def get_url(num):
    Session = sessionmaker(bind=engine)
    session = Session()

    # get url
    for c in session.query(Url).filter(Url.url_id == num).all():
        return c
    session.close()


def __str__(value):
    return f'{value}'


# Получение фото по id пользователя
def get_photos(num):
    Session = sessionmaker(bind=engine)
    session = Session()
    content_list = []

    for c in session.query(Photo).filter(Photo.photo_id == num).all():
        content_list.append(__str__(c))
    session.close()
    return content_list


def get_name_with_id():
    Session = sessionmaker(bind=engine)
    session = Session()
    content_dir = {}
    name = session.query(Name).all()
    id = session.query(Name.id).all()

    calc = 0
    for _ in zip(id, name):
        content_dir['{}'.format(*id[calc])] = __str__(name[calc])
        calc += 1
    return content_dir


def get_all_info(num):
    content_dir = {}
    name = get_name(num)
    url = get_url(num)
    photos = get_photos(num)
    content_dir['name'] = __str__(name)
    content_dir['url'] = __str__(url)
    content_dir['photos'] = __str__(photos)
    return content_dir


# Удаление пользователя по id
def delete_info(num):
    Session = sessionmaker(bind=engine)
    session = Session()
    name = get_name(num)
    if name != None:
        session.query(Url).filter(Url.url_id == num).delete()
        session.query(Photo).filter(Photo.photo_id == num).delete()
        session.query(Name).filter(Name.id == num).delete()
    session.commit()
    session.close()
    return f'Пользователь {name} успешно удален из избранных'


if __name__ == '__main__':
    name = ''
    url = ''
    photos = []
    num = 1
    create_tables(engine)
    # add_info()
    # get_name(1)
    # get_url(1)
    # get_photos(1)
    # print(delete_info(2))
    # add_info('Danil Dzuba', 'htsdoijfdds/dasokjdsia',
    #          ['dsadasdsa', 'sdadasdsadas'])
    # print(get_all_info(3))
    # print(get_name_with_id())
