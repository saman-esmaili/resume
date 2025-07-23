from django import forms
from datetime import date
from auths.models import Meal


class AddMealForm(forms.ModelForm):
    class Meta:
        model = Meal
        fields = ['name', 'category', 'price', 'amount', 'img_url', 'description', 'discount']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'نام غذا'}),
            'category': forms.TextInput(attrs={'placeholder': 'دسته بندی'}),
            'price': forms.NumberInput(attrs={'placeholder': 'قیمت'}),
            'amount': forms.TextInput(attrs={'placeholder': 'تعداد'}),
            'img_url': forms.FileInput(attrs={'class': 'form-control'}),
            'description': forms.TextInput(attrs={'placeholder': 'توضیحات کوتاهی در مورد غذا بنویسید'}),
            'discount': forms.NumberInput(attrs={'placeholder': 'تخفیف'})
        }

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        name = cleaned_data.get('name')
        if name == "" or name is None:
            self.add_error('name', 'غیلد نام غذا را پر کنید')

        category = cleaned_data.get('category')
        if category == "" or category is None:
            self.add_error('category', 'غیلد دسته بندی را پر کنید')

        price = cleaned_data.get('price')
        if price == "" or price is None:
            self.add_error('price', 'غیلد قیمت را پر کنید')

        amount = cleaned_data.get('amount')
        if amount == "" or amount is None:
            self.add_error('amount', 'غیلد تعداد را پر کنید')

        description = cleaned_data.get('description')
        if description == "" or description is None:
            self.add_error('description', 'غیلد توضیحات را پر کنید')

        if len(description) > 45:
            self.add_error('description', 'حداکثر کاراکتر مجاز 45 است')
        elif len(description) == 0:
            self.add_error('description', 'فیلد را پرکنید')

        return cleaned_data

    def clean_img_url(self):
        image = self.cleaned_data.get('img_url')
        if image:
            try:
                width, height = image.image.width, image.image.height
                max_height = 700
                max_width = 700
                if width > max_width or height > max_height or width - height > 200:
                    self.add_error('img_url', 'طول و عرض عکس نباید از 700 بیشتر شود')

                max_size = 500
                if image.size > max_size * 1024:
                    self.add_error('img_url', 'سایز عکس نباید از 500 کیلوبایت بیشتر شود')
            except Exception as er:
                print(er)
            return image
        self.add_error('img_url', 'لطفا تصویری انتخاب کنید')

    def save(self, commit=True):
        meal = super(AddMealForm, self).save(commit=False)
        meal.name = self.cleaned_data['name']
        meal.amount = self.cleaned_data['amount']
        meal.price = self.cleaned_data['price']
        meal.category = self.cleaned_data['category']
        meal.img_url = self.cleaned_data['img_url']
        meal.description = self.cleaned_data['description']
        meal.discount = self.cleaned_data['discount']
        meal.time_create = date.today()
        meal.price_discount = self.cleaned_data['price'] - (
                    (self.cleaned_data['discount'] / 100) * self.cleaned_data['price'])
        if commit:
            meal.save()
        return meal


class UsersSearchForm(forms.Form):
    search_user = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'عبارت'}), required=False)


class MealSearchForm(forms.Form):
    phrase = forms.CharField(widget=forms.TextInput(attrs={'placeholder': "عبارت"}), required=False)
    low_price = forms.IntegerField(widget=forms.NumberInput(attrs={'placeholder': 'از'}), required=False)
    high_price = forms.IntegerField(widget=forms.NumberInput(attrs={'placeholder': 'تا'}), required=False)


class UpdateMealForm(forms.ModelForm):
    class Meta:
        model = Meal
        fields = ['name', 'category', 'price', 'amount', 'img_url', 'description', 'discount']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'نام غذا'}),
            'category': forms.TextInput(attrs={'placeholder': 'دسته بندی'}),
            'price': forms.NumberInput(attrs={'placeholder': 'قیمت'}),
            'amount': forms.TextInput(attrs={'placeholder': 'تعداد'}),
            'img_url': forms.FileInput(attrs={'class': 'form-control'}),
            'description': forms.TextInput(attrs={'placeholder': 'توضیحات کوتاهی در مورد غذا بنویسید'}),
            'discount': forms.NumberInput(attrs={'placeholder': 'تخفیف'})
        }

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        name = cleaned_data.get('name')
        if name == "" or name is None:
            self.add_error('name', 'غیلد نام غذا را پر کنید')

        category = cleaned_data.get('category')
        if category == "" or category is None:
            self.add_error('category', 'غیلد دسته بندی را پر کنید')

        price = cleaned_data.get('price')
        if price == "" or price is None:
            self.add_error('price', 'غیلد قیمت را پر کنید')

        amount = cleaned_data.get('amount')
        if amount == "" or amount is None:
            self.add_error('amount', 'غیلد تعداد را پر کنید')

        description = cleaned_data.get('description')
        if description == "" or description is None:
            self.add_error('description', 'غیلد توضیحات را پر کنید')

        if len(description) > 45:
            self.add_error('description', 'حداکثر کاراکتر مجاز 45 است')
        elif len(description) == 0:
            self.add_error('description', 'فیلد را پرکنید')

        return cleaned_data

    def clean_img_url(self):
        image = self.cleaned_data.get('img_url')
        if image:
            try:
                width, height = image.image.width, image.image.height
                max_height = 700
                max_width = 700
                if width > max_width or height > max_height or width - height > 200:
                    self.add_error('img_url', 'طول و عرض عکس نباید از 700 بیشتر شود')

                max_size = 500
                if image.size > max_size * 1024:
                    self.add_error('img_url', 'سایز عکس نباید از 500 کیلوبایت بیشتر شود')
            except Exception as er:
                print(er)
            return image
        self.add_error('img_url', 'لطفا تصویری انتخاب کنید')
