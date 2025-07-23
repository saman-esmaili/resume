from fastapi import Depends, HTTPException,status
from passlib.context import CryptContext
from typing import Annotated

# hash password
pwd_crypt = CryptContext(schemes=['bcrypt'], deprecated='auto')


def hashing(password:str) -> str:
    return pwd_crypt.hash(password)


def verify(hashed_pass:str, password:str) -> bool:
    return pwd_crypt.verify(password, hashed_pass)
