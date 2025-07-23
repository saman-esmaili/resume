from django.shortcuts import render


def index(request):
    return render(request, 'auth/index.html',{'page':'index'})

def contact(request):
    return render(request,'auth/contact.html',{'page':'contact'})

def error_404(request):
    return render(request,'auth/404.html')

def checkout(request):
    return render(request, 'auth/checkout.html')