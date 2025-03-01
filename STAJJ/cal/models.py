#code influenced from github tutorial for implementing a calendar 
# github found at https://github.com/huiwenhw/django-calendar
#additions and changes were made to that code to suit needs of our project

#filter documentation at https://django-filter.readthedocs.io/en/stable/guide/usage.html#the-model

# Create your models here.
from django.db import models

from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone

from django.core.validators import URLValidator
from django.core.exceptions import ValidationError

class Event(models.Model):
    hide = models.BooleanField(default=False)
    title = models.TextField()
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    location = models.TextField(
        default = "University of South Carolina"
    )
    description = models.TextField(
        default = "User Added Event"
    )
    personal_event = models.BooleanField(
        default = False
    )
    posting_User_email = models.TextField(default="Web Scraped")
    TAGS = (
        ('UofSC Event','UofSC Event'),
        ('Columbia Event', 'Columbia Event'),
        ('Athletic Event','Athletic Event'),
        ('Club Event', 'Club Event'),
        ('Miscellaneous', 'Miscellaneous'),
    )
    filterTag = models.TextField(
        choices = TAGS,
        default = 'None'
    )
    
    @property
    def get_html_url(self):
        current_tz = timezone.get_current_timezone()
        url = reverse('cal:event_details', args=(self.id,))
        return f'<a href="{url}"> {self.title} {self.start_time.astimezone(current_tz).strftime("%H:%M")}</a>'

    @property
    def get_personal_html_url(self):
        current_tz = timezone.get_current_timezone()
        url = reverse('cal:personal_event_details', args=(self.id,))
        return f'<a href="{url}"> {self.title} {self.start_time.astimezone(current_tz).strftime("%H:%M")}</a>'
    
    @property
    def get_edit_html_url(self):
        current_tz = timezone.get_current_timezone()
        url = reverse('cal:event_edit', args=(self.id,))
        return f'<a href="{url}"> {self.title} {self.start_time.astimezone(current_tz).strftime("%H:%M")}</a>'

    @property
    def get_personal_edit_html_url(self):
        current_tz = timezone.get_current_timezone()
        url = reverse('cal:personal_event_edit', args=(self.id,))
        return f'<a href="{url}"> {self.title} {self.start_time.astimezone(current_tz).strftime("%H:%M")}</a>'

    @property
    def get_list_url(self):
        url = reverse('cal:event_details', args=(self.id,))
        return f'<a href="{url}"> {self.title}</a>'

    @property
    def get_personal_list_url(self):
        url = reverse('cal:personal_event_details', args=(self.id,))
        return f'<a href="{url}"> {self.title}</a>'

    @property
    def get_edit_list_url(self):
        url = reverse('cal:event_edit', args=(self.id,))
        return f'<a href="{url}"> {self.title}</a>'
    
    @property
    def get_personal_edit_list_url(self):
        url = reverse('cal:personal_event_edit', args=(self.id,))
        return f'<a href="{url}"> {self.title}</a>'
    
    @property
    def valid_url(self):
        validate_url = URLValidator()  
        try:
            validate_url(self.description)
        except (ValidationError):
            return self.description 
        return f'<a href="{ self.description }">Click for More Information</a>'