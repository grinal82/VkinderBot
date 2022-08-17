import sqlalchemy as sq
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class User(Base):
    """Класс создания таблицы 'user' """
    __tablename__ = 'user'
    #  Добавляем данные по юзеру бота
    id = sq.Column(sq.Integer, primary_key=True)
    user_id = sq.Column(sq.Integer, nullable=False, unique=True)


class Selected(Base):
    """
Таблица анкет пользователь добавленных в "избранное"
    """
    __tablename__ = 'selected_user'
    id = sq.Column(sq.Integer, primary_key=True, autoincrement=True)
    vk_id = sq.Column(sq.Integer, unique=True)
    first_name = sq.Column(sq.String)
    last_name = sq.Column(sq.String)
    link = sq.Column(sq.String)
    id_user = sq.Column(sq.Integer, sq.ForeignKey('user.id',
                                                  ondelete='CASCADE'))


class Photo(Base):
    """
    Класс создания таблицы 'photo' 
    """
    __tablename__ = 'photo'

    id = sq.Column(sq.Integer, primary_key=True, autoincrement=True)
    photo = sq.Column(sq.String)
    photo_id = sq.Column(sq.Integer,
                         sq.ForeignKey('selected_user.id', ondelete='CASCADE'))

    def __str__(self):
        return f'{self.photo}'
