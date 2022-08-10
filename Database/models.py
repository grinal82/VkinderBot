import sqlalchemy as sq
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()



class Name(Base):
    """Класс создания таблицы 'name' """
    __tablename__ = 'name'

    id = sq.Column(sq.Integer, primary_key=True)
    name = sq.Column(sq.String, nullable=False)

    def __str__(self):
        return f'{self.name}'



class Url(Base):
    """Класс создания таблицы 'url' """
    __tablename__ = 'url'

    id = sq.Column(sq.Integer, primary_key=True)
    url = sq.Column(sq.String, nullable=False)
    url_id = sq.Column(sq.Integer, sq.ForeignKey('name.id'), nullable=False)

    relation = relationship(Name, backref='url')

    def __str__(self):
        return f'{self.url}'



class Photo(Base):
    """Класс создания таблицы 'photo' """
    __tablename__ = 'photo'

    id = sq.Column(sq.Integer, primary_key=True)
    photo = sq.Column(sq.String)
    photo_id = sq.Column(sq.Integer, sq.ForeignKey('name.id'), nullable=False)

    relation = relationship(Name, backref='photo')

    def __str__(self):
        return f'{self.photo}'
