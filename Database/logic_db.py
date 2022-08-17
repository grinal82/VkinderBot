import os
import sqlalchemy
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
from dotenv import load_dotenv
from Database.models import Base, User, Photo, Selected, User

load_dotenv('.env')
login = os.getenv("LOGIN")
password = os.getenv("PASSWORD")
db_name = os.getenv("DB_NAME")

DSN = f"postgresql://{login}:{password}@localhost:5432/{db_name}"
engine = sqlalchemy.create_engine(DSN)


# function for start create table
def create_tables(engine):
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)


def add_user(user_id):
    """
    Args:
        user_id (int): id юзера vkontakte 

    Returns:
        boolean: добавляет vk id пользователя 
    """
    try:
        new_user = User(user_id=user_id)
        Session = sessionmaker(bind=engine)
        session = Session()
        session.add(new_user)
        session.commit()
        return True
    except (IntegrityError):
        return False


def add_info(vk_id, first_name, last_name, link, id_user):
    """
    Функция добавляет информацию о полученном человеке в базу данных
    """
    try:
        new_user = Selected(vk_id=vk_id,
                            first_name=first_name,
                            last_name=last_name,
                            link=link,
                            id_user=id_user)
        Session = sessionmaker(bind=engine)
        session = Session()
        session.add(new_user)
        session.commit()
        return True
    except (IntegrityError):
        return False


def add_photo(photo, photo_id):
    try:
        new_user = Photo(photo=photo, photo_id=photo_id)
        Session = sessionmaker(bind=engine)
        session = Session()
        session.add(new_user)
        session.commit()
        return True
    except (IntegrityError):
        return False


def check_favorite(id):
    """
    Вывод из БД отобранных пользователей  
    """
    Session = sessionmaker(bind=engine)
    session = Session()
    current_user_id = session.query(User).filter_by(user_id=id).first()
    all_users = session.query(Selected).filter_by(
        id_user=current_user_id.id).all()
    return all_users


def check_db_master(id):
    """
    выводим номер записи текущего юзера в БД 
    """
    Session = sessionmaker(bind=engine)
    session = Session()
    current_user_id = session.query(User).filter_by(user_id=id).first()
    return current_user_id


def check_candidate(id):
    """
    Проверка наличия текущего кандидата в БД 
    """
    Session = sessionmaker(bind=engine)
    session = Session()
    selected_user = session.query(Selected).filter_by(vk_id=id).first()
    return selected_user