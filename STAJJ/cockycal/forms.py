from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.forms import ModelForm, DateInput
from .models import Image, TaskItem
from cockycal.models import Image 
from users.models import Profile
from users.forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm, EditProfileForm

#form that handles images 
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
        resized_image = cropped_image.resize((200, 200), Image.ANTIALIAS)
        resized_image.save(photo.image.path)

        return photo
    #cleans the image to resize 
    def clean_image(self):
        image_field = self.cleaned_data.get('image')
        if image_field:
            try:
                image_file = BytesIO(image_field.file.read())
                image = Image.open(image_file)
                image.thumbnail((300, 300), Image.ANTIALIAS)
                image_file = BytesIO()
                image.save(image_file, 'PNG')
                image_field.file = image_file
                image_field.image = image

                return image_field
            except IOError:
                logger.exception("Error during resize image")
#update the profile image on profile page   
class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['image']
        
class ItemForm(ModelForm):
  class Meta:
    model = TaskItem
    # datetime-local is a HTML5 input type, format to make date time show on fields
    widgets = {
      'due_date': DateInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
    }
    fields = ["task_list", "title", "description", "due_date","completed"]

  def __init__(self, *args, **kwargs):
    super(ItemForm, self).__init__(*args, **kwargs)
    # input_formats to parse HTML5 datetime-local input to datetime field
    self.fields['due_date'].input_formats = ('%Y-%m-%dT%H:%M',)
    
  def save(self,commit=True):
    m = super(ItemForm, self).save(commit=False)
    # do custom stuff
    m.title = m.title.replace("<"," ").replace(">"," ")
    m.description = m.description.replace("<","").replace(">"," ")
    if commit:
        m.save()
    return m
#form to edit info in profile 
class EditProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['name','occupation','birthday','phonenumber']

        



        
