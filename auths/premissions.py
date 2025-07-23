from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import render

from auths.models import User


class LoginRequired(LoginRequiredMixin,UserPassesTestMixin):
    def test_func(self):
        pass

class AdminLoginRequired(LoginRequiredMixin,UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_superuser

    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            return render(self.request,'auth/404.html',status=403)
        return super().handle_no_permission()

class CheckLogin(LoginRequiredMixin,UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated