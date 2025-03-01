from pyexpat.errors import messages
from django.shortcuts import redirect, render
from django.http import HttpResponse
from django import forms 
from django.urls import reverse, reverse_lazy
from django.contrib.auth.decorators import login_required

# Create your views here.

def mainmenu(request):
    return render(request, 'mainpage/mainmenu.html')

def mainlogin(request):
    return render(request, 'cockycal/home.html')

def signup(request):
    return render(request, 'accounts/signup.html')

def register(request):
    return render(request, 'users/register.html')

def login(request):
    return render(request, 'users/login.html')

def aboutus(request):
    return render(request, 'mainpage/aboutus.html')

def learnmore(request):
    return render(request, 'mainpage/learnmore.html')

