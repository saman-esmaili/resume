from django import forms


class SearchMealForm(forms.Form):
    searchInput = forms.CharField(widget=forms.TextInput(attrs={'placeholder':'نام غذا'}),required=False)