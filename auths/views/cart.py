from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, DeleteView
from datetime import datetime
from auths.models import Order, OrderDetail, Meal, User, Discount, UserDiscount
from auths.premissions import LoginRequired, AdminLoginRequired
import sys
# for solve problem in farsi
sys.stdout.reconfigure(encoding='utf-8')

class ShowInCart(LoginRequiredMixin,ListView):
    template_name = 'auth/cart.html'
    model = OrderDetail
    def get(self, request, *args, **kwargs):
        user_id = self.request.user
        try:
            order = Order.objects.get(user_id=user_id,state='inProgress')
            if order.state == 'inProgress':
                data = OrderDetail.objects.filter(order_id=order.id).select_related('meal')
                total_price = 0
                for item in data:
                    total_price += (item.meal.price_discount*item.quantity)
            else:
                data = []
                total_price = 0
        except Order.DoesNotExist:
            data = []
            total_price = 0
        request.session['total_price'] = total_price
        request.session['number_food'] = len(data)
        return render(request, 'auth/cart.html', {'data': data})

    def post(self,request,*args,**kwargs):
        user_id = request.POST.get('txtUserId')
        meal_id = request.POST.get('txtMealId')
        meal = Meal.objects.get(id=meal_id)
        user = User.objects.get(id=user_id)
        try:
            order = Order.objects.filter(user=user,state='inProgress').get()
        except Order.DoesNotExist:
            order = Order(user=user, date=datetime.now().date())
            order.save()
        if order.state == 'inProgress':
            # find item by .first()
            orderDetail = OrderDetail.objects.filter(order_id=order, meal_id=meal).first()
            if orderDetail:
                orderDetail.quantity += 1
            else:
                orderDetail = OrderDetail(order_id=order.id, meal_id=meal_id)
            orderDetail.price = orderDetail.quantity * meal.price_discount
            orderDetail.save()
            data = OrderDetail.objects.filter(order_id=order).select_related('meal')
            total_price = 0
            for item in data:
                total_price += (item.meal.price_discount * item.quantity)
        else:
            total_price = 0
            data = []
        request.session['total_price'] = int(total_price)
        request.session['number_food'] = len(data)
        return redirect('menu')

def update_quantity(request):
    orderDetailId = request.POST.get('txtOrderDetailId')
    orderDetail = OrderDetail.objects.filter(id=orderDetailId).first()
    meal_id = orderDetail.meal
    meal = Meal.objects.filter(id=meal_id.id).first()
    price = meal.price_discount
    action = request.POST.get('action')
    order_detail = OrderDetail.objects.filter(id=orderDetailId).get()
    if action == '+':
        order_detail.quantity += 1
    elif action == '-':
        if order_detail.quantity > 1:
            order_detail.quantity -= 1
    order_detail.price = price * order_detail.quantity
    order_detail.save()
    return redirect('cart')


class DeleteOrderDetail(LoginRequiredMixin,DeleteView):
    model = OrderDetail
    login_url = 'login'
    template_name = 'auth/confirm_delete.html'
    success_url = reverse_lazy('cart')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['food_selected'] = context.pop('object')
        return context


    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request,'غذای انتخاب شده با موفقیت حذف شد')
        return response

def complete_purchase(request):
    user_id = request.user
    try:
        order = Order.objects.filter(user_id=user_id).get()
        if order.state == 'inProgress':
            order.state = 'complete'
            given_code = request.session.get('discount_code')
            try:
                find_discount = Discount.objects.filter(code=given_code).first()
                if find_discount:
                    user_discount = UserDiscount(user_id=user_id.id, discount_id=find_discount.id)
                    total = request.session.get('total_price')
                    total_dis = (total) - (total * find_discount.percent)
                    request.session['total_price'] = int(total_dis)
                    user_discount.save()
            except Discount.DoesNotExist:
                pass
            order.save()
        else:
            return redirect('cart')
    except Order.DoesNotExist:
        print('لیست سفارشی وجود ندارد')
    return redirect('checkout')


def discount(request):
    user_id = request.user
    given_code = request.POST.get('txtCode')
    find_discount = Discount.objects.filter(code=given_code).first()
    if find_discount:
        user_dis = UserDiscount.objects.filter(user_id=user_id.id,discount_id=find_discount.id)
        if user_dis:
            messages.error(request, 'این کد استفاده شده است',extra_tags='cart')
            return redirect('cart')
        else:
            if not request.session.get('discount_code'):
                request.session['discount_code'] = given_code
            percentage = find_discount.percent
            messages.success( request,f'شما دارای {int(percentage*100)} درصد تخفیف هستید ',extra_tags='cart')
            return redirect('cart')
    else:
        messages.error(request,'این کد نامعتبر است',extra_tags='cart')
        return redirect('cart')