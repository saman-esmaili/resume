from typing import Annotated
import os
import uuid
from fastapi import Depends, HTTPException,status

from Router.login import authorization


async def RestaurantDep(payload:Annotated[authorization,Depends()]):
    if payload['type'] == 'restaurant':
        return True
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="it's not restaurant")

async def change_name(image):
    extension = os.path.splitext(image)[1]
    new_name = f"custom-res{uuid.uuid4().hex}{extension}"
    return new_name


async def save_image(image_name, image):
    path = 'restaurant-backend\\static\\images\\food_restaurant'
    os.makedirs(path, exist_ok=True)

    save_path = os.path.join(path, image_name)

    with open(save_path, 'wb') as file:
        content = await image.read()
        file.write(content)
