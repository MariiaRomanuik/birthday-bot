import os
from enum import Enum

from sqlalchemy import Column, Integer, String, Date, ForeignKey
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

engine = create_engine(f'sqlite:///{os.path.dirname(__file__)}//telegram_info.db', echo=True)
Session = sessionmaker(bind=engine)
session = Session()
Base = declarative_base()


class Person(Base):
    __tablename__ = 'person'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    birthday = Column(Date)
    category_id = Column(Integer, ForeignKey('category.id'))
    category = relationship('Category', back_populates='persons')
    user_id = Column(Integer, ForeignKey('user.chat_id'))
    user = relationship('User', back_populates='persons')


class Category(Base):
    __tablename__ = 'category'

    id = Column(Integer, primary_key=True)
    type = Column(String)  # category name
    persons = relationship('Person', order_by=Person.name, back_populates='category')


class User(Base):
    __tablename__ = "user"

    chat_id = Column(Integer, primary_key=True)
    name = Column(String)
    persons = relationship('Person', order_by=Person.name, back_populates="user")


class StatusType(Enum):
    UpdateUserName = "UUN"
    CreatePersonName = "CPN"
    CreatePersonBirthday = "CPB"
    CreatePersonCategory = "CPC"
    EditPerson = "EP"
    EditPersonName = "EPN"
    EditPersonBirthday = "EPB"
    EditPersonCategory = "EPC"
    DeletePerson = "DP"
    ShowBirthdays = "SB"


class UserStatus(Base):
    __tablename__ = 'user_status'

    user_id = Column(Integer, primary_key=True)
    status_type = Column(String)
    person_id = Column(Integer, ForeignKey('person.id'))
    person = relationship('Person')


Base.metadata.create_all(engine)


def save(entity):
    session.add(entity)
    session.commit()


def get_user_by_chat_id(chat_id):
    return session.query(User).filter_by(chat_id=chat_id).first()


def get_persons_by_user(user_id):
    return session.query(Person).filter_by(user_id=user_id).all()


def get_person_by_user_and_name(user_id, name):
    return session.query(Person).filter_by(user_id=user_id, name=name).first()


def get_person_by_id(person_id):
    return session.query(Person).filter_by(id=person_id).first()


def delete_person_by_id(person_id):
    session.query(Person).filter_by(id=person_id).delete()
    session.commit()


def get_category_by_type(category_type):
    return session.query(Category).filter_by(type=category_type).first()


def get_category_type_by_id(person_id):
    category_id = session.query(Person).filter_by(id=person_id).all()
    category_type = session.query(Category).filter_by(id=category_id).all()
    # person = session.query(Person).filter_by(id=person_id).all()
    if category_type:
        return category_type
    else:
        return ""


def get_current_status_type(user_id):
    status = session.query(UserStatus).filter_by(user_id=user_id).first()
    if status:
        return status.status_type
    else:
        return ""


def get_current_status(user_id):
    return session.query(UserStatus).filter_by(user_id=user_id).first()


def delete_current_status(user_id):
    session.query(UserStatus).filter_by(user_id=user_id).delete()
    session.commit()


def show_person_by_written_date(person):
    return session.query(Person).filter_by(name=person.name).all()
