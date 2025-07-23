import datetime
from email.policy import HTTP
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException,status
from fastapi.params import Path
from sqlalchemy import func, select
from Router.login import authorization
from database import sessionDep, FoodRestaurant, Restaurant, Food, Order, Status, OrderDetails

router = APIRouter()

CATEGORIES = {
    'main': 'غذای اصلی',
    'appetizer': 'پیش غذا',
    'dessert': 'دسر',
    'drink': 'نوشیدنی',
    'salad': 'سالاد'
}


@router.get('/menu')
async def get_menu(session:sessionDep):
    restaurant_food = session.query(FoodRestaurant, Food, Restaurant).join(
        Food, Food.id == FoodRestaurant.food
    ).join(
        Restaurant, Restaurant.id == FoodRestaurant.restaurant
    ).all()
    food_list = []
    for fr,food,restaurant in restaurant_food:
        tags = food.tags.split(' ')
        tags.append(CATEGORIES[food.category])
        for tag in tags:
            if tag == ' ' or tag == '':
                tag.strip()
        food = {
            'id':fr.id,
            'restaurant': restaurant.username,
            'name':food.name,
            'price': fr.price,
            'serve_time': fr.serve_time,
            # 'tags': food.tags,
            'description': food.short_description,
            'image': food.image,
            'categories': tags
        }
        food_list.append(food)
    return food_list

@router.post('/add/cart/{food_id}')
async def add_to_cart(payload:Annotated[authorization,Depends()],session:sessionDep,food_id:Annotated[int,Path()]):
    user_id = payload['id']
    food_restaurant = session.query(FoodRestaurant).filter(FoodRestaurant.food==food_id).first()
    food_quantity = food_restaurant.quantity-1

    order = session.query(Order).filter(Order.user==user_id,Order.status==Status.incomplete).first()
    if order is None:
        order = Order(
            user=user_id,
            total_price=0,
            trans_id='',
            date=datetime.date.today(),
            status=Status.incomplete,
            description=''
        )
        session.add(order)
        session.commit()
        session.refresh(order)

    order_id = session.query(Order).filter(Order.user==user_id,Order.status==Status.incomplete).first().id
    if food_quantity > -1:
        try:
            order_details = session.query(OrderDetails).filter(OrderDetails.food_restaurant==food_restaurant.id,OrderDetails.order==order_id).first()
            order_details.quantity += 1
            session.commit()
            session.refresh(order_details)
        except:
            order_details = OrderDetails(
                food_restaurant=food_restaurant.id,
                order=order_id,
                quantity=1
            )
            session.add(order_details)
            session.commit()
            session.refresh(order_details)

    else:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='quantity more than stock')



    sum_price = select(
        func.coalesce(func.sum(FoodRestaurant.price*OrderDetails.quantity),0)
    ).select_from(OrderDetails).join(FoodRestaurant, FoodRestaurant.id == OrderDetails.food_restaurant).where(
        OrderDetails.order == order_id
    )
    total_price = session.execute(sum_price).scalar_one()

    order.total_price = total_price
    session.commit()
    session.refresh(order)

    food_restaurant.quantity -= 1
    session.commit()
    session.refresh(food_restaurant)


@router.post('/remove/cart/{food_id}')
async def remove_from_cart(payload:Annotated[authorization,Depends()],session:sessionDep,food_id:Annotated[int,Path()]):
    user_id = payload['id']
    order = session.query(Order).filter(Order.user==user_id,Order.status==Status.incomplete).first()
    food_restaurant = session.query(FoodRestaurant).filter(FoodRestaurant.food==food_id).first()
    order_details = (
        session.query(OrderDetails)
        .join(FoodRestaurant, FoodRestaurant.id == OrderDetails.food_restaurant)
        .filter(
            OrderDetails.order == order.id,
            FoodRestaurant.food == food_id
        )
        .first()
    )

    food_restaurant.quantity += 1
    food_price = food_restaurant.price
    order.total_price -= food_price

    order_details.quantity -= 1
    if order_details.quantity <= 0:
        session.delete(order_details)


    session.commit()


@router.get('/load/cart')
async def load_cart(session:sessionDep,payload:Annotated[authorization,Depends()]):
    user_id = payload['id']

    stmt = (
        select(Order, OrderDetails, FoodRestaurant, Food,Restaurant)
        .join(OrderDetails, OrderDetails.order == Order.id)
        .join(FoodRestaurant, FoodRestaurant.id == OrderDetails.food_restaurant)
        .join(Food, Food.id == FoodRestaurant.food)
        .join(Restaurant,Restaurant.id == FoodRestaurant.restaurant)
        .where(Order.user == user_id)
    )
    items = session.execute(stmt).all()
    i=1
    result = []
    for order, order_detail,food_restaurant,food,restaurant in items:
        total = order.total_price
        cart = {
            'order_detail_id': order_detail.id,
            'restaurant_id': restaurant.id,
            'food_id': food.id,
            'food_price': food_restaurant.price,
            'food_name': food.name,
            'restaurant':restaurant.username,
            'quantity': order_detail.quantity,
            'description': food.short_description,
            'image': food.image
        }
        result.append(cart)
    result.append({'order':total})
    return result