import datetime
from datetime import timedelta
import pytest
from typing import Literal, Annotated, Optional
from pydantic import BaseModel, EmailStr
import jwt
from fastapi.testclient import TestClient
from fastapi.params import Body, Depends
import datetime
from datetime import time
from enum import Enum
from typing import Optional, Annotated, List
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import Session
from sqlmodel import SQLModel, Field

from Router.login import secret, ALGORITHM
from database import Restaurant, User, Situation, UserType, get_session
from dependenies import hashing
from main import app

client = TestClient(app)

def generate_token(data:dict):
    data = data.copy()
    data['exp'] = datetime.datetime.utcnow() + timedelta(minutes=10)
    create_token = jwt.encode(data,secret,algorithm=ALGORITHM)
    return create_token



def test_valid_token():
    token = generate_token({'username':'saman'})
    response = client.get('/authorization',headers={'Authorization':f'Bearer {token}'})
    assert response.status_code == 200
    data = response.json()
    assert data['username'] == 'saman'

def test_invalid_token():
    incorrect_token = 'jdsklgjioewsdj'
    response = client.get('/authorization',headers={'Authorization':f'Bearer {incorrect_token}'})
    assert response.status_code == 401
    assert response.json() == {'detail':'invalid token'}

def test_expired_token():
    expired_data = {'username': 'saman'}
    expired_data['exp'] = datetime.datetime.utcnow() - timedelta(seconds=1)
    expired_token = jwt.encode(expired_data, secret, algorithm=ALGORITHM)

    response = client.get('/authorization',headers={'Authorization':f'Bearer {expired_token}'})
    assert response.status_code == 401
    assert response.json() == {'detail':'expired token'}



DATABASE_URL = 'sqlite:///:memory:'
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False},poolclass=StaticPool)

def get_test_session():
    with Session(engine) as session:
        yield session

app.dependency_overrides = {}
app.dependency_overrides[get_session] = get_test_session


def create_db_table():
    SQLModel.metadata.create_all(engine)


def seed_data():
    with Session(engine) as session:
        user = User(
            username="saman",
            email="saman@test.com",
            phone="09120000000",
            password=hashing("saman123"),
            type='customer'
        )
        restaurant = Restaurant(
            username='saman',
            email="saman@test.com",
            phone='09145564545',
            password=hashing('saman'),
            situation=Situation.waiting,
            address='tehran',
            category='fastfood',
        )
        restaurant2 = Restaurant(
            username='saman2',
            email="saman3@test.com",
            phone='09145564546',
            password=hashing('saman'),
            situation=Situation.approved,
            category='fastfood',
            address='tehran'
        )
        session.add_all([user, restaurant, restaurant2])
        session.commit()


@pytest.fixture(autouse=True)
def prepare_db():
    create_db_table()
    seed_data()
    yield

def test_success_login():
    payload = {
        "username": "09120000000",
        'password': 'saman123',
        'type': 'customer',
    }
    response = client.post('/login',json=payload)
    assert response.status_code == 200
    data = response.json()
    assert 'access_token' in data



def test_not_approved_restaurant():
    payload = {
        "username": "09145564545",
        'password': 'saman',
        'type': 'restaurant',
    }
    response = client.post('/login',json=payload)
    assert response.status_code == 403
    assert response.json() == {'detail':'not approved'}


def test_success_login_restaurant():
    payload = {
        "username": "09145564546",
        'password': 'saman',
        'type': 'restaurant',
    }

    response = client.post('/login',json=payload)
    assert response.status_code == 200
    data = response.json()
    assert 'access_token' in data

def test_user_login_not_found():
    payload = {
        "username": "09120000016",
        'password': 'saman123',
        'type': 'customer',
    }
    response = client.post('/login',json=payload)
    assert response.status_code == 404
    assert response.json() == {'detail':'Not Found'}

def test_restaurant_login_not_found():
    payload = {
        "username": "09145564999",
        'password': 'saman',
        'type': 'restaurant',
    }
    response = client.post('/login',json=payload)
    assert response.status_code == 404
    assert response.json() == {'detail':'Not Found'}