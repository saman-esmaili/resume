from typing import Annotated

from fastapi import APIRouter, Body, HTTPException, UploadFile, File, Form
from pydantic import BaseModel, Field
from sqlalchemy import select
from fastapi import status

from database import sessionDep, CreateUser, CreateRestaurant, User, Restaurant
from dependenies import hashing

router = APIRouter()


class Info(BaseModel):
    username: str
    email: str
    password: str
    address: str = Field(default=None)
    category: str = Field(default=None)
    phone: str
    type: str


@router.post('/signup')
async def signup(data: Annotated[Info, Body()], session: sessionDep):
    if data.type == 'customer':
        existence = session.query(User).filter(User.phone == data.phone, User.email == data.email).first()
        if existence:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='User is exist')
        await register_customer(data,session)
    else:
        existence = session.query(Restaurant).filter(Restaurant.phone == data.phone,
                                                             Restaurant.email == data.email).first()
        if existence:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='Restaurant is exist')
        await register_restaurant(data,session)

async def register_customer(data,session):
    hashed_pass = hashing(data.password)
    user = User(
        username=data.username,
        email= data.email,
        phone= data.phone,
        password= hashed_pass
    )
    session.add(user)
    session.commit()
    session.refresh(user)

async def register_restaurant(data,session):
    hashed_pass = hashing(data.password)
    data_dict = data.dict()
    data_dict['password'] = hashed_pass
    restaurant = Restaurant(**data_dict)
    session.add(restaurant)
    session.commit()
    session.refresh(restaurant)



