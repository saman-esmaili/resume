from django.contrib.auth import forms
from django import forms
import re
from auths.models import User


class SignUpForm(forms.ModelForm):
    re_password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder':'تکرار گذرواژه*'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder':'گذرواژه*'}))

    class Meta:
        model = User
        fields = ['full_name', 'phone', 'password','mobile']
        widgets = {
            'full_name': forms.TextInput(attrs={'placeholder':'نام کامل شما*'}),
            'phone': forms.TextInput(attrs={'placeholder':'تلفن ثابت'}),
            'mobile': forms.TextInput(attrs={'placeholder':'123*****09'}),
        }

        def __init__(self,*args,**kwargs):
            super().__init__(*args,**kwargs)

    def clean(self):
        cleaned_data = super().clean()

        full_name = cleaned_data.get('full_name')
        if full_name == "" or full_name is None:
            self.add_error('full_name',"لطفا نام و نام خانوادگی خود را وارد کنید")
        phone = cleaned_data.get('phone')
        if phone == "" or phone is None:
            self.add_error('phone','لطفا تلفن ثابت خود را وارد کنید')

        phone_regex = r'^[1-9]+[0-9]{7}$'
        if not re.match(phone_regex,phone):
            self.add_error('phone','تلفن ثابت شما نامعتبر است')

        password = cleaned_data.get('password')
        password_regex = r'^[a-zA-Z0-9@_]{8,}$'
        re_password = cleaned_data.get('re_password')
        if password == "" or password is None:
            self.add_error('password', 'لطفا گذرواژه خود را وارد کنید')
        if re_password == "" or re_password is None:
            self.add_error('re_password', 'لطفا تکرار گذرواژه خود را وارد کنید')
        if password != re_password:
            self.add_error('password','گذرواژه با تکرار آن تطابق ندارد')

        if not re.match(password_regex, password):
            self.add_error('password','حداقل 8 کاراکتر , یک حرف بزرگ , یک حرف کوچک , یک عدد و @ یا _ باشد')

        mobile = cleaned_data.get('mobile')
        if mobile == "" or mobile is None:
            self.add_error('mobile', 'لطفا شماره همراه خود را وارد کنید')

        mobile_regex = r'^09[0-9]{9}$'
        if not re.match(mobile_regex,mobile):
            self.add_error('mobile','شماره همراه نامعتبر است')

        return cleaned_data


    def clean_mobile(self):
        mobile = self.cleaned_data.get('mobile')
        if User.objects.filter(mobile=mobile):
            self.add_error('mobile',"این شماره همراه قبلا استفاده شده است")
        return mobile


    def save(self, commit=True):
        user = super(SignUpForm,self).save(commit=False)
        user.full_name = self.cleaned_data['full_name']
        user.phone = self.cleaned_data['phone']
        user.mobile = self.cleaned_data['mobile']
        user.username = self.cleaned_data['mobile']
        user.set_password(self.cleaned_data['password'])

        if commit:
            user.save()
        return user
