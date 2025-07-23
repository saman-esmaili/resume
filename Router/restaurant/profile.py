from fastapi import APIRouter, Depends, UploadFile, File
from typing import Annotated

from Router.login import authorization
from Router.restaurant.dependencies import RestaurantDep, change_name, save_image
from database import sessionDep, Restaurant, PubRestaurant

router = APIRouter(prefix='/restaurant',
                   dependencies=[Depends(RestaurantDep)])

@router.get('/get/info')
async def get_info():
    return {'status':'ok'}



@router.post('/save/image')
async def save_restaurant_image(image:Annotated[UploadFile,File()],session:sessionDep,payload:Annotated[authorization,Depends()]):
    rest_id = payload['id']
    new_name = await change_name(image.filename)

    restaurant = session.query(Restaurant).get(rest_id)
    restaurant.image = new_name
    session.commit()
    session.refresh(restaurant)

    await save_image(new_name,image)




