import base64
import hashlib
from googleapiclient.errors import HttpError
import json
import os.path
import pickle
import random
from email.mime.text import MIMEText
from urllib.error import HTTPError
from requests import HTTPError
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import requests
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView
from google.auth.transport.requests import Request

from auths.forms.signup_form import SignUpForm
from auths.models import User, Meal, Order, OrderDetail
from auths.premissions import CheckLogin


class SignUp(CreateView):
    model = User
    template_name = 'auth/register.html'
    success_url = reverse_lazy('login')
    form_class = SignUpForm
    def form_valid(self, form):
        response = super().form_valid(form)
        return response

    def get(self, request, *args, **kwargs):
        if self.request.user.is_authenticated:
            return redirect('index')
        return super().get(request,*args,**kwargs)

class LoginView(TemplateView):
    template_name = 'auth/login.html'
    def post(self,request,*args,**kwargs):
        mobile = request.POST.get('mobile')
        password = request.POST.get('password')
        user = authenticate(request,username=mobile,password=password)
        if user and password != '':
            login(request,user)
            try:
                order = Order.objects.filter(user_id=user.id,state='inProgress').get()
                if order:
                    if order.state == 'inProgress':
                        data = OrderDetail.objects.filter(order_id=order.id)
                        request.session['number_food'] = len(data)
                    else:
                        request.session['number_food'] = 0
            except Order.DoesNotExist:
                request.session['number_food'] = 0
            return redirect('index')
        else:
            messages.error(self.request,'نام کاربری یا گذرواژه شما نادرست است')
            return render(request,'auth/login.html',{'page':'login'})

    def get(self,request,*args,**kwargs):
        if request.user.is_authenticated:
            return redirect('index')
        return render(request,'auth/login.html',{'page':'login'})

class LoginViewOtp(TemplateView):
    template_name = 'auth/login_otp.html'
    def post(self,request,*args,**kwargs):
        mobile = request.POST.get('mobile')
        user = User.objects.filter(mobile=mobile).first()
        # if mobile[0] == '0':
        #     mobile = mobile[1:]

        otp = request.POST.get('otp')
        if otp and otp != '':
            temp_otp = request.session['otp']
            if otp == str(temp_otp):
                if not user:
                    user = User()
                    user.mobile = mobile
                    user.save()
                login(request,user)
                try:
                    order = Order.objects.filter(user_id=user.id).get()
                    if order:
                        if order.state == 'inProgress':
                            data = OrderDetail.objects.filter(order_id=order.id)
                            request.session['number_food'] = len(data)
                        else:
                            request.session['number_food'] = 0
                except Order.DoesNotExist:
                    request.session['number_food'] = 0
                return redirect('index')
        else:
            otp = random.randint(100000,999999)
            result = send_otp(mobile,otp)
            if result.status_code == 200:
                request.session['otp'] = otp
                return render(request,self.template_name,{'otp':True,'mobile':mobile})
            else:
                return render(request,self.template_name,{'otp':False,'mobile':mobile})

    def get(self,request,*args,**kwargs):
        if request.user.is_authenticated:
            return redirect('index')
        return render(request,'auth/login_otp.html',{'page':'login'})

class EmailAuth(TemplateView):
    template_name = 'auth/login_email.html'
    def post(self,request,*args,**kwargs):
        email = request.POST.get('email')
        user = User.objects.filter(email=email).first()
        email_msg = request.POST.get('email_code')
        if email_msg and email_msg != '':
            temp_email_msg = request.session.get('temp_email_msg')
            if temp_email_msg == email_msg:
                if not user:
                    user = User()
                    user.username = email
                    user.email = email
                    user.save()
                login(request, user)
                try:
                    order = Order.objects.filter(user_id=user.id).get()
                    if order:
                        if order.state == 'inProgress':
                            data = OrderDetail.objects.filter(order_id=order.id)
                            request.session['number_food'] = len(data)
                        else:
                            request.session['number_food'] = 0
                except Order.DoesNotExist:
                    request.session['number_food'] = 0
                return redirect('index')
            else:
                return render(request,self.template_name)
        else:
            msg = random.randint(100000,999999)
            request.session['temp_email_msg'] = str(msg)
            send_email(email,msg)
            return render(request,self.template_name,{'email':email,'temp_email_msg': msg})
    def get(self,request,*args,**kwargs):
        if request.user.is_authenticated:
            return redirect('index')
        return render(request,'auth/login_email.html',{'page':'login'})

def logout_view(request):
    logout(request)
    return redirect('index')

class Cart(LoginRequiredMixin,TemplateView):
    template_name = 'auth/cart.html'
    login_url = 'login'


def send_otp(mobile,otp):
    base_url = 'https://api.sms.ir/v1/send/likeTolike'
    data = json.dumps({
        'lineNumber': 1,
        'messageTexts':[
            f"کد ورود به کابان: {str(otp)}"
        ],
        'mobiles':[
            mobile,
        ],
        'senddatetime': None
    })
    headers = {
        'content-Type': 'application/json',
        'Accept': 'text/plain',
        'X-API-KEY': 'key'
    }
    response = requests.post(url=base_url,data=data,headers=headers)
    return response

def send_email(user_email,msg):
    SCOPES = ["https://www.googleapis.com/auth/gmail.send"]
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
            print("Expiry:", creds.expiry)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('gmail', 'v1', credentials=creds)
    message = f'کد ورود شما به کابان : {msg}'
    message = MIMEText(message)
    message['to'] = str(user_email).strip()
    message['from'] = 'رستوران کابان'
    message['subject'] = 'ورود به کابان'

    create_message = {'raw': base64.urlsafe_b64encode(message.as_bytes()).decode()}

    try:
        sent_message = service.users().messages().send(userId="me", body=create_message).execute()
        print(F'sent message to {message["to"]} Message Id: {sent_message["id"]}')
    except HTTPError as error:
        print(F'An error occurred: {error}')
