# https://www.youtube.com/watch?v=q4jPR-M0TAQ&list=PL-osiE80TeTtoQCKZ03TU5fNfx2UY6U4p&index=6 
#used this tutorial to set up my user registration system


from django import forms
from .models import CustomUser
from django.contrib.auth.forms import UserCreationForm
from .models import Profile
from django.forms.widgets import NumberInput
from cockycal.models import Image 

#registers a user and ensures they use a usc email address 
class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()

# https://stackoverflow.com/questions/13240032/restrict-user-to-use-a-specific-domain-to-sign-up-django
# used this for making sure only usc email

    def clean_email(self):
        data = self.cleaned_data['email']
        if "@email.sc.edu" not in data:   # any check you need
            raise forms.ValidationError("Must be a USC email address")
        return data

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password1', 'password2']
        
#update a users username and email 
class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField()
    class Meta:
        model = CustomUser
        fields = ['username', 'email']

#form that is shown on profile page to update these fields 
class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['image','name','occupation','birthday','phonenumber']
   
#handles images uploaded on profile page      
class ImageForm(forms.ModelForm):
    image = forms.ImageField(
        widget=forms.FileInput(
        attrs={
            "class": "form-control"
        }
    ))
    x = forms.FloatField(widget=forms.HiddenInput())
    y = forms.FloatField(widget=forms.HiddenInput())
    width = forms.FloatField(widget=forms.HiddenInput())
    height = forms.FloatField(widget=forms.HiddenInput())
    class Meta:
        model = Image
        fields = ('title', 'image','x', 'y', 'width', 'height',)
        labels = {'user_image': ''},
        
    def save(self):
        photo = super(ImageForm, self).save()

        x = self.cleaned_data.get('x')
        y = self.cleaned_data.get('y')
        w = self.cleaned_data.get('width')
        h = self.cleaned_data.get('height')

        image = Image.open(photo.image)
        cropped_image = image.crop((x, y, w+x, h+y))
        resized_image = cropped_image.resize((300, 300), Image.ANTIALIAS)
        resized_image.save(photo.image.path)

        return photo

#editing the information on the profile page 
class EditProfileForm(forms.ModelForm):
    name = forms.CharField(widget=forms.Textarea())
    occupation = forms.CharField(widget=forms.Textarea())
    birthday = forms.DateField(widget=NumberInput(attrs={'type': 'date'}))
    phonenumber = forms.CharField(widget=forms.Textarea())
    class Meta:
        model = Profile
        fields = ['name','occupation','birthday','phonenumber']
        
     
    def save(self, commit=True):
            user = super(EditProfileForm, self).save(commit=False)
            if commit:
                user.profile.save()

            return user   
   
    