from django.urls import path,include
from auths.views import index, authentication, search, admin, add_to_cart, cart


urlpatterns = [
    path('',index.index,name='index'),

    # login and signup
    path('login/',authentication.LoginView.as_view(),name='login'),
    path('login_otp/',authentication.LoginViewOtp.as_view(),name='login_otp'),
    path('login-email/',authentication.EmailAuth.as_view(),name='login_email'),
    path('signup/',authentication.SignUp.as_view(),name='signup'),


    path('menu/',search.MealView.as_view(),name='menu'),
    path('contact/',index.contact,name='contact'),
    path('cart/',cart.ShowInCart.as_view(),name='cart'),
    path('checkout/',index.checkout,name='checkout'),
    path('update-quantity-food/',cart.update_quantity,name='update_quantity'),
    path('cart/delete-food/<int:pk>',cart.DeleteOrderDetail.as_view(),name='delete_order_detail'),
    path('complete-purchase/',cart.complete_purchase,name='complete_purchase'),
    path('cart/discount/',cart.discount,name='discount'),
    path('exit/',authentication.logout_view,name='exit'),


    # 404
    path('not-found/',index.error_404,name='error_404'),

    # admin
    path('menu/add_meal/',admin.AddMeal.as_view(),name='add_meal'),
    path('admin-dashboard/',admin.AdminDashboard.as_view(),name='admin_dashboard'),
    path('user-address/<int:pk>',admin.UserAddress.as_view(),name='user_address'),
    path('admin-delete-meal/<int:pk>',admin.DeleteMeal.as_view(),name='delete_meal'),
    path('admin-update-meal/<int:pk>',admin.UpdateMeal.as_view(),name='update_meal'),
    path('meal-list',admin.MealList.as_view(),name='meal_list'),
    path('order-list/<int:pk>',admin.OrderList.as_view(),name='order_list'),
]