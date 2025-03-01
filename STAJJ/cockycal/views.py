from pyexpat.errors import messages
from django.shortcuts import redirect, render
from django.http import HttpResponseRedirect
from django import forms 
from django.views import generic
from .forms import ImageForm, ItemForm
from .models import TaskItem
from django.urls import reverse, reverse_lazy
from django.utils.safestring import mark_safe
from django.views.generic import (
    ListView,
    CreateView,
    UpdateView,
    DeleteView,
)
from django.template.response import TemplateResponse
from datetime import datetime
import csv
import requests
from cal.models import Event
from cal.utils import EventList
from django.utils import timezone
from django.utils.safestring import mark_safe
from users.utils import upcoming_events, weekly_events, upcoming_tasks
from users.views import profile
from users.forms import UserCreationForm, UserRegisterForm, ProfileUpdateForm
from users.models import Profile, CustomUser
from django.contrib.auth.decorators import login_required
from datetime import datetime, timedelta, date
from cal.utils import EventCalendar
from cal.models import Event
from django.contrib.auth.mixins import LoginRequiredMixin

# Create your views here.

@login_required (login_url='login')
def home(request):
    api_key = 'fa321620cd169c7e6b9d92c2786d4cce'
    url = f'https://api.openweathermap.org/data/2.5/forecast/daily?q=Columbia,South Carolina&cnt=7&appid={api_key}&units=imperial'
    weather_data = None
    result = requests.get(url).json()
    user = CustomUser.objects.get(pk=request.user.pk)
    if "city" in result:
        weather_forecast = []
        for i,item in enumerate(result['list']):
            weather_data = {
                'date': datetime.fromtimestamp(item['dt']).strftime("%m-%d-%Y"),
                'temp_high': item['temp']['max'],
                'temp_low': item['temp']['min'],
                'description': item['weather'][0]['description'],
                'icon': item['weather'][0]['icon'],
            }
            weather_forecast.append(weather_data)
    upcoming = upcoming_events(user)
    tasks = upcoming_tasks(user)
    if request.method == 'POST':
        if request.POST.getlist('delete_event') is not None:
            event_ids = request.POST.getlist('delete_event')
            for event in user.events_attending.all():  
                if str(event.pk) in event_ids:
                    user.events_attending.remove(event)
                    user.upcoming_events.remove(event)
                    event.hide = True
                    event.save()                    
                    user.save()
        elif request.POST.getlist('task_completed') is not None:
            task_complete = request.POST.getlist('task_completed')
            for task in task_complete:
                comp_task = TaskItem.objects.filter(pk=task)
                for instance in comp_task:
                    instance.completed = True
                    instance.save()
        return redirect('/home')
    context = {'weather_forecast': weather_forecast,
              'upcoming': upcoming,
              'tasks' : tasks
              }
    return TemplateResponse(request, 'cockycal/home.html', context)
    
def eventcal(request):
    return render(request, 'cockycal/eventcal.html')

def personalcal(request):
    return render(request, 'cockycal/personalcal.html')

@login_required (login_url='login')
def tasklist(request):
    return render(request, 'cockycal/tasklist.html')

def signup(request):
    return render(request, 'accounts/signup.html')

def register(request):
    return render(request, 'users/register.html')

def login(request):
    return render(request, 'users/login.html')

@login_required (login_url='login')
def profile(request):
    user = CustomUser.objects.get(pk=request.user.pk)

    if request.method == 'POST':
        p_form = ProfileUpdateForm(request.POST,
                                   request.FILES,
                                   instance=request.user.profile)
        if p_form.is_valid():
            p_form.save()
            #return redirect('cockycal/profile.html')
    else:
        p_form = ProfileUpdateForm(instance=request.user.profile)
    weekly = weekly_events(user)
    context = {
        'p_form':p_form, 
        'weekly':weekly,
    }
    return TemplateResponse(request, 'cockycal/profile.html', context)

# This creates the list of tasks for each category 
class ItemListView(LoginRequiredMixin,ListView):
    login_url = 'login'
    model = TaskItem
    template_name = "cockycal/tasklist.html"

    def get_queryset(self):
        # This filters the queryset to only display the user's tasks
        user = CustomUser.objects.get(pk=self.request.user.pk)
        return TaskItem.objects.filter(author=user)
    
    def get_context_data(self):
        context = super().get_context_data()
        context["general_tasks"] = TaskItem.objects.filter(task_list='General Tasks').filter(author=self.request.user)
        context["pri_tasks"] = TaskItem.objects.filter(task_list='Priority Tasks').filter(author=self.request.user)
        context["class_tasks"] = TaskItem.objects.filter(task_list='Class Tasks').filter(author=self.request.user)
        context["misc_tasks"] = TaskItem.objects.filter(task_list='Misc. Tasks').filter(author=self.request.user)
        return context

# Creating a new item to be added to the task list
class ItemCreate(LoginRequiredMixin,CreateView):
    model = TaskItem
    form_class = ItemForm
    login_url = 'login'

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.is_valid()
        return super().form_valid(form)
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        return kwargs

    def get_context_data(self):
        context = super(ItemCreate, self).get_context_data()
        context["title"] = "Create A New Task"
        return context
    
    def get_success_url(self):
        return reverse_lazy('cockycal-tasklist')

# Updating an item in the existing task list
class ItemUpdate(LoginRequiredMixin,UpdateView):
    model = TaskItem
    form_class = ItemForm
    login_url = 'login'

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.is_valid()
        return super().form_valid(form)
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        return kwargs

    def get_context_data(self):
        context = super(ItemUpdate, self).get_context_data()
        context["task_list"] = self.object.task_list
        context["title"] = "Edit Task"
        return context

    def get_success_url(self):
        return reverse_lazy('cockycal-tasklist')

# Deleting an item in the task list
class ItemDelete(LoginRequiredMixin,DeleteView):
    model = TaskItem
    login_url = 'login'

    def get_success_url(self):
        return reverse_lazy('cockycal-tasklist')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["task_list"] = self.object.task_list
        return context
    
def edit_profile(request):
    if request.method == "POST":
        e_form = EditProfileForm(request.POST,instance=request.user.profile)
        if e_form.is_valid():
            name=  e_form.cleaned_data["name"]
            occupation =  e_form.cleaned_data["occupation"]
            birthday =  e_form.cleaned_data["birthday"]
            phonenumber = e_form.cleaned_data["phonenumber"]
            
            user.profile.save()
            e_form.save()
    else:
        e_form = EditProfileForm()
    return render(request, 'profile.html', {'e_form': e_form})