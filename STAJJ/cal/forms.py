# using tutorial, github found at https://github.com/huiwenhw/django-calendar

from django.forms import ModelForm, DateInput
from cal.models import Event

from django import forms 


class EventForm(forms.ModelForm):
  class Meta:
    model = Event
    # datetime-local is a HTML5 input type, format to make date time show on fields
    widgets = {
      'start_time': DateInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
      'end_time': DateInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
    }
    fields = ["title", "location","description", "start_time", "end_time", "filterTag",]

  def clean(self):
    # data from the form is fetched using super function
    super(EventForm, self).clean()
      
    start_time = self.cleaned_data.get('start_time')
    end_time = self.cleaned_data.get('end_time')
    if start_time > end_time:
      raise forms.ValidationError('End time must occur after Start time')
    return self.cleaned_data

        

  def __init__(self, *args, **kwargs):
    super(EventForm, self).__init__(*args, **kwargs)
    # input_formats to parse HTML5 datetime-local input to datetime field
    self.fields['start_time'].input_formats = ('%Y-%m-%dT%H:%M',)
    self.fields['end_time'].input_formats = ('%Y-%m-%dT%H:%M',)
  
  def save(self, commit=True):
    m = super(EventForm, self).save(commit=False)
    # do custom stuff
    m.title = m.title.replace("<"," ").replace(">"," ")
    m.location = m.location.replace("<","").replace(">"," ")
    m.description = m.description.replace("<","").replace(">"," ")
    if commit:
        m.save()
    return m
