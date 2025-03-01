
from django.shortcuts import render, redirect
from django.contrib import messages
from users.forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm, EditProfileForm
from django.core.mail import send_mail, BadHeaderError
from django.http import HttpResponse
from django.contrib.auth.forms import PasswordResetForm
from django.template.loader import render_to_string
from django.db.models.query_utils import Q
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from .models import CustomUser
from cal.models import Event
from .utils import add_event_to_user
from django.shortcuts import get_object_or_404
from .models import Profile
# Create your views here.
#https://www.youtube.com/watch?v=q4jPR-M0TAQ&list=PL-osiE80TeTtoQCKZ03TU5fNfx2UY6U4p&index=6 
#used this tutorial to set up my user registration system
def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            user = form.save()
            profile = Profile()
            profile.user = user
            #profile.save()
            messages.success(request, f'Account created for {username}! You can now login')
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'users/register.html', {'form': form})


#updating a users profile 
def profile(request):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST,
                                   request.FILES,
                                   instance=request.user.profile)
        e_form = EditProfileForm(request.POST,instance=request.user.profile)
        if u_form.is_valid() and p_form.is_valid() and e_form.is_valid():
            u_form.save()
            p_form.save()
            e_form.save()
            messages.success(request, f'Your account has been updated!')
            return redirect('cockycal/profile.html')

    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)

    context = {
        'u_form': u_form,
        'p_form': p_form
    }

    return render(request, 'cockycal/profile.html', context)


def add_event(request,event_id):
    user= CustomUser.objects.get(pk=request.user.pk)

    # Create a new event

    # Call the add_event_to_user function
    add_event_to_user(request, pk=event_id)

    # Render a template to display the user's events
    events = user.events_attending.all()
    return render(request, 'added.html', {'events': events})


# Change contents stored in the user's profile information#editing users profile information
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
    context = {
        'e_form': e_form
    }
    return render(request, 'profile.html', {'e_form': e_form})
