import os.path
import uuid
from typing import Annotated, Optional

import jwt
from fastapi import APIRouter, HTTPException, UploadFile, File, status
from fastapi.params import Depends, Body, Form, Path
from pydantic import BaseModel

from Router.login import oauth2, secret, ALGORITHM, authorization
from Router.restaurant import profile
from Router.restaurant.dependencies import RestaurantDep, change_name, save_image
from database import sessionDep, Food, FoodRestaurant, Order, Status

router = APIRouter(prefix='/restaurant',
                   dependencies=[Depends(RestaurantDep)])

@router.get('/add/food')
async def get_add_food():
    return {"add_food": "access"}


@router.post('/add/food')
async def add_food(payload: Annotated[authorization, Depends()], session: sessionDep,
                   name: Annotated[str, Form()],
                   price: Annotated[int, Form()],
                   quantity: Annotated[int, Form()],
                   description: Annotated[str, Form()],
                   tags: Annotated[str, Form()],
                   serve_time: Annotated[str, Form()],
                   category: Annotated[str, Form()],
                   image: Annotated[UploadFile, File()]):
    restaurant_id = payload['id']
    search_food = session.query(Food).filter(Food.name == name, Food.category == category, Food.tags == tags
                                             , Food.short_description == description).first()
    if search_food:
        search_food_restaurant = session.query(FoodRestaurant).filter(FoodRestaurant.food == search_food.id,
                                                                      FoodRestaurant.restaurant == restaurant_id).first()
        if search_food_restaurant:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='food exist')

    if payload['type'] == 'restaurant':
        dict_data = {
            'name': name,
            'short_description': description,
            'tags': tags,
            'category': category,
            'image': image
        }
        await add_food_to_food_table(session, dict_data)

        food = session.query(Food).filter(Food.name == name, Food.category == category, Food.tags == tags
                                          , Food.short_description == description).first()

        data = {
            'restaurant': restaurant_id,
            'food': food.id,
            'price': price,
            'serve_time': serve_time,
            'quantity': quantity
        }
        await add_food_restaurant(session, data)




async def add_food_to_food_table(session, dict_data):
    image_info = dict_data['image']
    image_name = await change_name(image_info.filename)

    dict_data['image'] = image_name

    food = Food(**dict_data)
    session.add(food)
    session.commit()
    session.refresh(food)

    await save_image(image_name, image_info)


async def add_food_restaurant(session, data):
    food_restaurant = FoodRestaurant(**data)

    session.add(food_restaurant)
    session.commit()
    session.refresh(food_restaurant)


CATEGORIES = {
    'main': 'غذای اصلی',
    'appetizer': 'پیش غذا',
    'dessert': 'دسر',
    'drink': 'نوشیدنی',
    'salad': 'سالاد'
}


# list of food
@router.get('/foods')
async def foods(payload: Annotated[authorization, Depends()], session: sessionDep):
    rest_id = payload['id']
    result = []
    query = (
        session.query(FoodRestaurant, Food).join(
            Food, FoodRestaurant.food == Food.id
        ).filter(FoodRestaurant.restaurant == rest_id)
    )

    rows = query.all()
    for food_rest, food in rows:
        food_dict = {
            'id': food.id,
            'name': food.name,
            'price': food_rest.price,
            'quantity': food_rest.quantity,
            'description': food.short_description,
            'category': CATEGORIES[food.category],
            'image': food.image
        }
        result.append(food_dict)

    return result


# remove food
@router.delete('/delete/food/{food_id}')
async def remove_food(session: sessionDep, food_id: Annotated[int, Path()]):
    selected_food_rest = session.query(FoodRestaurant).filter(FoodRestaurant.food == food_id).first()
    session.delete(selected_food_rest)

    selected_food = session.query(Food).filter(Food.id == food_id).first()
    image = selected_food.image
    session.delete(selected_food)
    session.commit()

    await delete_image(image)


async def delete_image(image):
    path = f'restaurant-backend\\static\\images\\food_restaurant\\{image}'
    if os.path.exists(path):
        os.remove(path)


# edit food
@router.get('/edit/food/{food_id}')
async def get_edit_food(payload:Annotated[authorization,Depends()],food_id: Annotated[int, Path()], session: sessionDep):
    food = session.query(Food).get(food_id)
    rest_id = payload['id']
    restaurant_food = session.query(FoodRestaurant).filter(FoodRestaurant.food == food_id,FoodRestaurant.id==rest_id).first()

    result = {
        'name': food.name,
        'description': food.short_description,
        'category': food.category,
        'price': restaurant_food.price,
        'quantity': restaurant_food.quantity,
        'serve_time': restaurant_food.serve_time,
        'image': food.image,
        'tags': food.tags
    }

    return result


@router.put('/edit/food/{food_id}')
async def edit_food(payload:Annotated[authorization,Depends()],food_id:Annotated[int,Path()],
                    session:sessionDep,
                    name:Annotated[str,Form()],
                    price:Annotated[int,Form()],
                    tags:Annotated[str,Form()],
                    description:Annotated[str,Form()],
                    quantity:Annotated[int,Form()],
                    serve_time:Annotated[str,Form()],
                    category:Annotated[str,Form()],
                    image:Annotated[Optional[UploadFile],File()] = None):
    rest_id = payload['id']
    food = session.query(Food).get(food_id)
    image_db = food.image
    food.name = name
    food.tags = tags
    food.category = category
    food.short_description = description
    if image:
        changed_name = await change_name(image.filename)
        food.image = changed_name
        await save_image(changed_name,image)
        await delete_image(image_db)

    session.commit()
    session.refresh(food)

    food_restaurant = session.query(FoodRestaurant).filter(FoodRestaurant.food==food_id,FoodRestaurant.id==rest_id).first()

    food_restaurant.price = price
    food_restaurant.quantity = quantity
    food_restaurant.serve_time = serve_time

    session.commit()
    session.refresh(food)


# increase and decrease quantity of foods
@router.put('/food/increase/{food_id}')
async def increase_food_quantity(payload:Annotated[authorization,Depends()],food_id:Annotated[int,Path()],session:sessionDep):
    rest_id = payload['id']
    restaurant_food = session.query(FoodRestaurant).filter(FoodRestaurant.restaurant ==rest_id, FoodRestaurant.food==food_id).first()

    restaurant_food.quantity += 1
    session.commit()
    session.refresh(restaurant_food)


@router.put('/food/decrease/{food_id}')
async def increase_food_quantity(payload: Annotated[authorization, Depends()], food_id: Annotated[int, Path()],
                                 session: sessionDep):
    rest_id = payload['id']
    restaurant_food = session.query(FoodRestaurant).filter(FoodRestaurant.restaurant == rest_id, FoodRestaurant.food == food_id).first()
    restaurant_food.quantity -= 1
    session.commit()
    session.refresh(restaurant_food)


