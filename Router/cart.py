from typing import Annotated

from fastapi import APIRouter
from fastapi.params import Depends,Path
from Router.login import authorization
from database import sessionDep, FoodRestaurant, OrderDetails, Order, Status

router = APIRouter(prefix='/cart')

@router.post('/remove/food/{food_id}')
async def cart_food(payload:Annotated[authorization,Depends()],session:sessionDep,food_id:Annotated[int,Path()]):
    user_id = payload['id']
    order = session.query(Order).filter(Order.user == user_id,Order.status==Status.incomplete).first()
    order_id = order.id

    row = (
        session.query(OrderDetails,FoodRestaurant)
        .join(FoodRestaurant,FoodRestaurant.id == OrderDetails.food_restaurant)
        .filter(
            OrderDetails.order == order.id,
            FoodRestaurant.food == food_id
        )
        .first()
    )
    order_details,food_restaurant = row


    quantity = order_details.quantity
    food_restaurant.quantity += quantity
    price = food_restaurant.price
    total_price = quantity*price
    order.total_price -= total_price

    session.delete(order_details)
    session.commit()
