from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
import os
from Router import signup, login, menu, cart
from Router.restaurant import menu_management, profile
from database import create_db_table
from starlette.staticfiles import StaticFiles


app = FastAPI()

app.mount('/static/images/food_restaurant',StaticFiles(directory='restaurant-backend\\static\\images\\food_restaurant'),name='static')


app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*']
)

app.include_router(menu.router)
app.include_router(menu_management.router)
app.include_router(profile.router)
app.include_router(login.router)
app.include_router(signup.router)
app.include_router(cart.router)

@app.on_event('startup')
def startup():
    if not os.environ.get("TEST_MODE"):
        create_db_table()