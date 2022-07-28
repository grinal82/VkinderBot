import sqlalchemy as sq
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


# create table 'name'
class Name(Base):
    __tablename__ = 'name'

    id = sq.Column(sq.Integer, primary_key=True)
    name = sq.Column(sq.String, nullable=False)

    def __str__(self):
        return f'{self.name}'


# create table 'url'
class Url(Base):
    __tablename__ = 'url'

    id = sq.Column(sq.Integer, primary_key=True)
    url = sq.Column(sq.String, nullable=False)
    url_id = sq.Column(sq.Integer, sq.ForeignKey('name.id'), nullable=False)

    relation = relationship(Name, backref='url')

    def __str__(self):
        return f'{self.url}'


# create table 'photo'
class Photo(Base):
    __tablename__ = 'photo'

    id = sq.Column(sq.Integer, primary_key=True)
    photo = sq.Column(sq.String)
    photo_id = sq.Column(sq.Integer, sq.ForeignKey('name.id'), nullable=False)

    relation = relationship(Name, backref='photo')

    def __str__(self):
        return f'{self.photo}'
