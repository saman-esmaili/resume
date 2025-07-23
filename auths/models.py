from django.contrib.auth.models import AbstractUser
from django.db import models

from auths.storage import MealStorage


class User(AbstractUser):
    full_name = models.CharField(max_length=60,blank=False,null=False)
    phone = models.CharField(max_length=11,null=True,blank=True)
    mobile = models.CharField(max_length=11,null=True,blank=True)
    type = models.CharField(max_length=10,null=True,blank=True)

class Order(models.Model):
    STATE = ['inProgress','cancel','complete']
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    date = models.DateField(max_length=10,null=True,blank=True)
    state = models.CharField(max_length=20,null=False,blank=False,default=STATE[0])
    total_price = models.FloatField(max_length=10,null=True,blank=True)
    discount = models.FloatField(max_length=3,null=True,blank=True)
    is_payment = models.BooleanField(null=True,blank=True)
    is_delivered = models.BooleanField(null=True,blank=True)
    payment_date = models.DateField(max_length=10,null=True,blank=True)
    trans_id = models.CharField(max_length=50,null=True,blank=True)

class Meal(models.Model):
    name = models.CharField(max_length=30,null=False,blank=False)
    category = models.CharField(max_length=30,null=False,blank=False)
    price = models.IntegerField(null=False,blank=False)
    price_discount = models.IntegerField(null=True,blank=True)
    amount = models.IntegerField(null=False,blank=False)
    discount = models.IntegerField(null=True,blank=True,default=0)
    img_url = models.ImageField(upload_to='images',null=True,blank=True,storage=MealStorage)
    time_create = models.DateField(null=True,blank=True)
    description = models.CharField(max_length=45,null=True,blank=False)

class OrderDetail(models.Model):
    order = models.ForeignKey(Order,on_delete=models.CASCADE)
    meal = models.ForeignKey(Meal,on_delete=models.CASCADE)
    price = models.FloatField(max_length=10,null=False,blank=False,default=0)
    quantity = models.IntegerField(null=False,blank=False,default=1)
    shipping = models.FloatField(max_length=7,null=False,blank=False,default=0)

class Comment(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    comment = models.CharField(max_length=500,null=True,blank=True)
    date = models.DateField(max_length=10,null=True,blank=True)

class Address(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    address = models.CharField(max_length=100,null=False,blank=False)
    latitude = models.CharField(max_length=10,null=False,blank=False)
    longitude = models.CharField(max_length=10,null=False,blank=False)

class Discount(models.Model):
    code = models.CharField(max_length=10,null=False,blank=False)
    percent = models.FloatField(max_length=3,null=False,blank=False)
    expired_date = models.DateField(max_length=10,null=True,blank=True)
    usage = models.IntegerField(null=False,blank=False)

class UserDiscount(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    discount = models.ForeignKey(Discount,on_delete=models.CASCADE)
    count = models.IntegerField(null=True,blank=True)