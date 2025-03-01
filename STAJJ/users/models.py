
#users.models

from django import forms
from django.db import models
from PIL import Image
from django.contrib.auth.models import AbstractUser
from django.forms import ValidationError
from cal.models import Event
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.validators import MaxValueValidator, MinValueValidator 
from phonenumber_field.modelfields import PhoneNumberField




class CustomUser(AbstractUser):
    events_attending = models.ManyToManyField(Event,related_name='all_events',blank=True)
    upcoming_events = models.ManyToManyField(Event,related_name='upcoming_events',blank=True)
    email = models.EmailField(unique=True)

#this model handles all the fields in the users profile that are displayed 
class Profile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    image = models.ImageField(default='default.png', upload_to='profile_pics')
    name = models.CharField(default='', max_length=40)
    occupation = models.CharField(default='', max_length=40)
    birthday = models.DateField(default='1900-01-01')
    #phonenumber = models.PositiveIntegerField(verbose_name="Phone number",default='', validators=[MinValueValidator(1000000000),MaxValueValidator(9999999999)])
    phonenumber = PhoneNumberField(blank=True,verbose_name="Phone number",region="US")

    def __str__(self):
        return f'{self.user.username} Profile'
    
    
    ''' def save(self, *args, **kwargs):
       super().save()
       
       img = Image.open(self.image.path)
       
       if img.height > 300 or img.width > 300:
            output_size = (300, 300)
            img.thumbnail(output_size)
            img.save(self.image.path)  '''
#https://stackoverflow.com/questions/54545621/how-to-resize-and-crop-an-image-into-a-square-in-django
#used this for image resizing 
    def save(self, *args, **kwargs):
        super().save()
        img = Image.open(self.image.path)

        # When image height is greater than its width
        if img.height > img.width:
            # make square by cutting off equal amounts top and bottom
            left = 0
            right = img.width
            top = (img.height - img.width)/2
            bottom = (img.height + img.width)/2
            img = img.crop((left, top, right, bottom))
            # Resize the image to 300x300 resolution
            if img.height > 300 or img.width > 300:
                output_size = (300, 300)
                img.thumbnail(output_size)
                img.save(self.image.path)

        # When image width is greater than its height
        elif img.width > img.height:
            # make square by cutting off equal amounts left and right
            left = (img.width - img.height)/2
            right = (img.width + img.height)/2
            top = 0
            bottom = img.height
            img = img.crop((left, top, right, bottom))
            # Resize the image to 300x300 resolution
            if img.height > 300 or img.width > 300:
                output_size = (300, 300)
                img.thumbnail(output_size)
                img.save(self.image.path)
            

    @receiver(post_save, sender=CustomUser)
    def create_profile(sender, instance, created, **kwargs):
        if created:
            Profile.objects.create(user=instance)
