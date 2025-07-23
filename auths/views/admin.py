from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q, Sum,F,Case,When,Value,CharField
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, DeleteView,UpdateView

from auths.forms.admin_form import AddMealForm, UsersSearchForm, MealSearchForm, UpdateMealForm
from auths.models import Meal, User, Address, Order
from auths.premissions import AdminLoginRequired, LoginRequired
from django.core.cache import cache

class AddMeal(AdminLoginRequired, CreateView):
    template_name = 'auth/add_meal.html'
    login_url = 'login'
    success_url = reverse_lazy('menu')
    form_class = AddMealForm
    model = Meal

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'غذا با موفقیت افزوده شد')
        return response


class AdminDashboard(AdminLoginRequired, ListView):
    template_name = 'auth/admin_dashboard.html'
    login_url = 'error_404'
    model = User
    context_object_name = 'users'
    paginate_by = 10
    form_class = UsersSearchForm

    def get_queryset(self):
        queryset = User.objects.annotate(total_spent=Sum(F('order__orderdetail__price')),
                                         price_category=Case(
                                             When(total_spent__gte=700000, then=Value('طلایی')),
                                             When(total_spent__gte=400000,total_spent__lt=700000, then=Value('نقره ای')),
                                             When(total_spent__lt=400000,then=Value('برنزی')),
                                             default=Value('-'),
                                             output_field=CharField()
                                         )
                                         ).order_by('id')
        form = UsersSearchForm(self.request.GET)
        if form.is_valid():
            query = form.cleaned_data['search_user']
            if query:
                queryset = queryset.filter(Q(full_name__icontains=query) |
                                           Q(mobile__icontains=query) |
                                           Q(address__address__icontains=query) |
                                           Q(price_category__icontains=query)).order_by('id')
        return queryset

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['form'] = UsersSearchForm(self.request.GET)
        return context


class UserAddress(AdminLoginRequired, ListView):
    model = Address
    template_name = 'auth/address_user.html'
    def get_context_data(self,**kwargs):
        context = super(UserAddress,self).get_context_data(**kwargs)
        pk = self.kwargs['pk']
        address = Address.objects.filter(user_id=pk)
        context['address'] = address
        return context


class DeleteMeal(AdminLoginRequired,DeleteView):
    template_name = 'auth/admin_confirm_delete.html'
    model = Meal
    login_url = 'login'
    success_url = reverse_lazy('menu')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['meal_selected'] = context.pop('object')
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        return response

class MealList(AdminLoginRequired,ListView):
    template_name = 'auth/list_meal.html'
    model = Meal
    context_object_name = 'meals'
    login_url = 'error_404'
    paginate_by = 10
    form_class = MealSearchForm

    def get_queryset(self):
        queryset = Meal.objects.order_by('-time_create')
        form = MealSearchForm(self.request.GET)
        if form.is_valid():
            phrase = form.cleaned_data['phrase']
            low_price = form.cleaned_data['low_price']
            high_price = form.cleaned_data['high_price']
            if phrase:
                queryset = queryset.filter(Q(name__icontains=phrase) |
                                           Q(category__icontains=phrase) |
                                           Q(description__icontains=phrase))
            elif low_price and high_price:
                queryset = queryset.filter(Q(price__gt=low_price) &
                                           Q(price__lt=high_price))
            return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = MealSearchForm(self.request.GET)
        return context


class UpdateMeal(AdminLoginRequired,UpdateView):
    model = Meal
    template_name = 'auth/update_meal.html'
    form_class = UpdateMealForm
    success_url = reverse_lazy('meal_list')
    login_url = 'error_404'

    def get_object(self):
        meal_instance = super().get_object()
        return meal_instance
    def form_valid(self, form):
        response = super().form_valid(form)
        return response

class OrderList(AdminLoginRequired, ListView):
    model = Order
    template_name = 'auth/order_list.html'
    def get_context_data(self,**kwargs):
        context = super(OrderList,self).get_context_data(**kwargs)
        pk = self.kwargs['pk']
        order = Order.objects.filter(user_id=pk)
        context['orders'] = order
        return context