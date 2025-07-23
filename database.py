import datetime
from datetime import time
from enum import Enum
from typing import Optional, Annotated, List

from fastapi import Depends
from pydantic import EmailStr
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlmodel import SQLModel, Field


class UserType(str, Enum):
    user = 'user'
    admin = 'admin'


class BaseUser(SQLModel):
    username: Optional[str] = Field(default=None, min_length=3)


class User(BaseUser, table=True):
    id: int = Field(default=None, primary_key=True)
    email: EmailStr
    phone: str = Field(min_length=11, max_length=11, regex=r'^09[0-3,9]\d{8}$')
    password: str
    type: str = Field(default=UserType.user)


class CreateUser(BaseUser):
    email: EmailStr
    phone: Optional[str] = Field(min_length=11, max_length=11, regex=r'^09[0-3,9]\d{8}$')
    password: Optional[str]


class UpdateUser(BaseUser):
    username: Optional[str] = Field(default=None, min_length=5)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(default=None, min_length=11, max_length=11, regex=r'^09[0-3,9]\d{8}$')
    password: Optional[str] = None


class Situation(str, Enum):
    waiting = 'waiting'
    approved = 'approved'
    rejected = 'rejected'


class BaseRestaurant(SQLModel):
    username: str = Field(min_length=3)
    category: str



class Restaurant(BaseRestaurant, table=True):
    id: int = Field(default=None, primary_key=True)
    email: EmailStr
    phone: str = Field(min_length=11, max_length=11, regex=r'^09[0-3,9]\d{8}$')
    password: str
    situation: str = Field(default=Situation.waiting)
    image: Optional[str] = Field(default=None,nullable=True)
    address: str
    closing_time: Optional[time] = Field(default=None,nullable=True)
    day_off: Optional[str] = Field(default=None,nullable=True)


class PubRestaurant(BaseRestaurant):
    email: EmailStr
    phone: str = Field(min_length=11, max_length=11, regex=r'^09[0-3,9]\d{8}$')
    image: Optional[str] = Field(default=None, nullable=True)
    address: str
    closing_time: Optional[time] = Field(default=None, nullable=True)
    day_off: Optional[str] = Field(default=None, nullable=True)


class CreateRestaurant(BaseRestaurant):
    email: EmailStr
    phone: str = Field(min_length=11, max_length=11, regex=r'^09[0-3,9]\d{8}$')
    password: str
    situation: str = Field(default=Situation.waiting)
    image: Optional[str] = Field(default=None)
    address: str
    closing_time: Optional[time] = Field(default=None)
    day_off: Optional[str] = Field(default=None)



class UpdateRestaurant(BaseRestaurant):
    email: Optional[EmailStr]
    phone: Optional[str] = Field(min_length=11, max_length=11, regex=r'^09[0-3,9]\d{8}$')
    password: Optional[str]
    situation: Optional[str] = Field(default=Situation.waiting)
    image: Optional[str]
    address: Optional[str]
    closing_time: time = Field(default=None)
    day_off: Optional[str] = Field(default=None)


class Address(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    address: str = Field(min_length=10)
    longitude: str = Field(default=None)
    latitude: str = Field(default=None)
    user: int = Field(foreign_key='user.id')


class Food(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    name: str
    ingredient: str = Field(default=None,nullable=True)
    short_description: str
    description: str = Field(default=None,nullable=True)
    image: str
    category: str
    tags: str

class UpdateFood(SQLModel):
    name: Optional[str]
    ingredient: Optional[str] = Field(default=None)
    short_description: Optional[str]
    description: Optional[str] = Field(default=None)
    image: Optional[str]


class FoodRestaurant(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    restaurant: int = Field(foreign_key='restaurant.id')
    food: int = Field(foreign_key='food.id')
    price: int = Field(gt=1000)
    quantity: int
    serve_time: str


class Comment(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    rate: float = Field(gt=0, le=5)
    comment: str = Field(min_length=3)
    food: int = Field(foreign_key='food.id')
    restaurant: int = Field(foreign_key='restaurant.id')
    user: int = Field(foreign_key='user.id')


class Status(str, Enum):
    paid = 'paid'
    canceled = 'canceled'
    incomplete = 'incomplete'


class Order(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    user: int = Field(foreign_key='user.id')
    total_price: int
    trans_id: str
    description: str = Field(default=None)
    date: datetime.date
    status: str = Field(default=Status.incomplete)

class OrderDetails(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    food_restaurant: int = Field(foreign_key='foodrestaurant.id')
    order: int = Field(foreign_key='order.id')
    quantity: int



database_name = 'database.db'
database_url = f'sqlite:///{database_name}'
connect_args = {'check_same_thread': False}

engine = create_engine(database_url, connect_args=connect_args)


async def get_session():
    with Session(engine) as session:
        yield session


sessionDep = Annotated[Session, Depends(get_session)]


def create_db_table():
    SQLModel.metadata.create_all(engine)
