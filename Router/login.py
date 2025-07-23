import datetime
from datetime import timedelta
from typing import Annotated, Literal
from fastapi import status, Depends
import jwt
from fastapi import APIRouter, Body, HTTPException
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel

from database import sessionDep, Restaurant, User, Status, Situation
from dependenies import verify

router = APIRouter()

with open('secret.txt','r') as file:
    secret = file.read()
ALGORITHM = 'HS256'

oauth2 = OAuth2PasswordBearer(tokenUrl='login')

class Info(BaseModel):
    username: str
    password: str
    type: Literal['customer','restaurant']

@router.post('/login')
async def login(data:Annotated[Info,Body()],session:sessionDep):
    if data.type == 'restaurant':
        result = session.query(Restaurant).filter(Restaurant.phone == data.username).first()
        if not result:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Not Found')
        if result.situation != Situation.approved:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail='not approved')
    else:
        result = session.query(User).filter(User.phone == data.username).first()

    if result:
        verified = verify(result.password,data.password)
        if verified:
            payload = {
                'id': result.id,
                'type': data.type,
                'username':data.username,
                'exp': datetime.datetime.utcnow() + timedelta(minutes=30)
            }
            access_token = jwt.encode(payload,secret,algorithm=ALGORITHM)
            return {'access_token':access_token,'token_type':'bearer'}
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail='Not Found')


@router.get('/authorization')
async def authorization(token:Annotated[oauth2,Depends()]):
    try:
        payload = jwt.decode(token,secret,algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail='expired token')
    except jwt.PyJWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='invalid token')


    