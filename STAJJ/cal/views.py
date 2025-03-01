# using tutorial at https://github.com/huiwenhw/django-calendar


# Create your views here.

from datetime import datetime, timedelta, date
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, HttpRequest
from django.views import generic
from django.urls import reverse
from django.utils.safestring import mark_safe
import calendar

from .utils import EventCalendar, PersonalCalendar, EventList, PersonalList
from .filter import EventFilter
from .models import Event
from .forms import EventForm
from users.models import CustomUser
from cockycal.models import TaskItem
from django.contrib.auth.decorators import login_required

from users.utils import add_event_to_user, remove_event_from_user
from django.contrib.auth.mixins import LoginRequiredMixin

#Class to generate views for the Event Calendar

class EventCalendarView(LoginRequiredMixin,generic.ListView):
    login_url = 'login'
    model = Event
    template_name = 'cal/eventcalendar.html'

    #Upon request returns data for the view as elements of a context list that are called in cal/eventcalendar.html
    def get_context_data(self, **kwargs):
        date = get_date(self.request.GET.get('month', None))

        context = super().get_context_data(**kwargs)
        events = Event.objects.all().order_by('start_time')

        filtered_events, eventfilter = apply_filter(events, self.request.GET)
        user = self.request.user

        cal = EventCalendar(events, date.year, date.month)
        html_cal = cal.formatmonth(user, eventlist=filtered_events, withyear=True)
        legend = cal.legend()
        context['prev_month'] = prev_month(date)
        context['next_month'] = next_month(date)
        #creates context for the from the string created in EventCalendar formatmonth from Utils using Mark Safe
        context['eventcalendar'] = mark_safe(html_cal)
        context['eventfilter'] = eventfilter.form
        context['month'] = str(date.year) + '-' + str(date.month)
        context['legend'] = mark_safe(legend)
        #get applied filter to pass through get request if filter is not empty
        try: 
            context['filterParams'] = "&title="+self.request.GET.get('title') + "&" + "location="+self.request.GET.get('location') + "&" + "filterTag="+self.request.GET.get('filterTag')
        except:
            context['filterParams'] = ""
        return context


class PersonalCalendarView(LoginRequiredMixin,generic.ListView):
    login_url = 'login'
    model = Event
    template_name = 'cal/personalcalendar.html'

    #Upon request returns data for the view as elements of a context list that are called in cal/personalcalendar.html
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        date = get_date(self.request.GET.get('month', None))
        cal = PersonalCalendar(date.year, date.month)
        user = self.request.user
        try:
            events = user.events_attending.all().order_by('start_time')
        except:
            events = Event.objects.all().filter(title="Not a Real Event")
        filtered_events, eventfilter = apply_filter(events, self.request.GET)
        cal = PersonalCalendar(events, date.year, date.month)
        task_list = TaskItem.objects.filter(author=user)
        html_cal = cal.formatmonth(user, events=filtered_events, tasks_list=task_list, withyear=True)
        legend = cal.legend()
        #creates context for the from the string created in PersonalCalendar formatmonth from Utils using Mark Safe
        context['personalcalendar'] = mark_safe(html_cal)
        context['eventfilter'] = eventfilter.form
        context['prev_month'] = prev_month(date)
        context['next_month'] = next_month(date)
        context['legend'] = mark_safe(legend)
        try: 
            context['filterParams'] = "&title="+self.request.GET.get('title') + "&" + "location="+self.request.GET.get('location') + "&" + "filterTag="+self.request.GET.get('filterTag')
        except:
            context['filterParams'] = ""
        context['month'] = str(date.year) + '-' + str(date.month)
        
        return context

#If passed a month, it returns a date in the month, otherwise returns the current date 
def get_date(req_month):
    if req_month:
        year, month = (int(x) for x in req_month.split('-'))
        return date(year, month, day=1)
    return datetime.today()

#Logic for previous month button returns month prior to month passed to it 
def prev_month(d):
    first = d.replace(day=1)
    prev_month = first - timedelta(days=1)
    month = 'month=' + str(prev_month.year) + '-' + str(prev_month.month)
    return month

#Logic for next month button returns month after the month passed to it 
def next_month(d):
    days_in_month = calendar.monthrange(d.year, d.month)[1]
    last = d.replace(day=days_in_month)
    next_month = last + timedelta(days=1)
    month = 'month=' + str(next_month.year) + '-' + str(next_month.month)
    return month

#View for creating a new event and posting to the event calendar
def event(request, event_id=None):
    #creates an instance of an event
    instance = Event()
    #if event already exists it returns the data for that object, otherwise creates new event
    if event_id:
        instance = get_object_or_404(Event, pk=event_id)
    else:
        instance = Event()
        instance.posting_User_email = request.user.email
        form = EventForm(request.POST or None, instance=instance)
        if request.POST and form.is_valid():
            form.save()
            add_event_to_user(request,instance.pk)
            return HttpResponseRedirect(reverse('cal:cockycal-eventcal'))
        return render(request, 'cal/event.html', {'form': form})
    #adds event to the list of event calendar events
    form = EventForm(request.POST or None, instance=instance)
    if request.POST and 'Delete' in request.POST:
            instance.delete()
            return HttpResponseRedirect(reverse('cal:cockycal-eventcal'))
    if request.POST and form.is_valid():
        form.save()
        return HttpResponseRedirect(reverse('cal:cockycal-eventcal'))
    if request.user.email == instance.posting_User_email:
        return render(request, 'cal/edit_event.html', {'form': form})
    return render(request, 'cal/event.html', {'form': form})

#View for creating a new event and posting to personal calendar
def pers_event(request, event_id=None):
    #creates an instance of an event
    instance = Event()
    #if event already exists it returns the data for that object, otherwise creates new event
    if event_id:
        instance = get_object_or_404(Event, pk=event_id)
    else:
        instance = Event()
        instance.personal_event = True
        instance.posting_User_email = request.user.email
        form = EventForm(request.POST or None, instance=instance)
        if request.POST and form.is_valid():
            form.save()
            add_event_to_user(request,instance.pk)
            return HttpResponseRedirect(reverse('cal:cockycal-personalcal'))
        return render(request, 'cal/event.html', {'form': form})
        
    #adds event to the list of event calendar events
    form = EventForm(request.POST or None, instance=instance)
    if request.POST and 'Delete' in request.POST:
            instance.delete()
            return HttpResponseRedirect(reverse('cal:cockycal-personalcal'))
    if request.POST and form.is_valid():
        form.save()
        add_event_to_user(request,instance.pk)
        if 'Delete' in request.POST:
            instance.delete() 
        return HttpResponseRedirect(reverse('cal:cockycal-personalcal'))
    if request.user.email == instance.posting_User_email:
        return render(request, 'cal/personal_edit_event.html', {'form': form})
    return render(request, 'cal/event.html', {'form': form})

#View for the details page when an event is clicked on
def event_details(request, event_id):
    #gets instance of event or throws forbidden error
    event = get_object_or_404(Event,pk=event_id)
    validated_url = event.valid_url
    #gets the current user
    user = request.user
    #Shows Remove event button if user has event on personal calendar
    if event in user.events_attending.all():
        if 'Remove' in request.POST:
            remove_event_from_user(request, event_id)
            return render(request, 'cal/event_details.html',{'event':event,'valid_url':mark_safe(validated_url)})
        return render(request, 'cal/added_event.html',{'event':event, 'valid_url':mark_safe(validated_url)})
    #Shows add event button if user does not have event on personal calendar
    if 'Add' in request.POST:
        add_event_to_user(request,event_id)
        return render(request, 'cal/added_event.html',{'event':event, 'valid_url':mark_safe(validated_url)})
    return render(request, 'cal/event_details.html',{'event':event, 'valid_url':mark_safe(validated_url)})

#View for the details page when an event is clicked on
def personal_event_details(request, event_id):
    #gets instance of event or throws forbidden error
    event = get_object_or_404(Event,pk=event_id)
    #gets the current user
    user = request.user
    validated_url = event.valid_url
    #Shows Remove event button if user has event on personal calendar
    if event in user.events_attending.all():
        if 'Remove' in request.POST:
            remove_event_from_user(request, event_id)
            return render(request, 'cal/personal_event_details.html',{'event':event, 'valid_url':mark_safe(validated_url)})
    #Shows add event button if user does not have event on personal calendar
    if 'Add' in request.POST:
        add_event_to_user(request,event_id)
        return render(request, 'cal/personal_added_event.html',{'event':event, 'valid_url':mark_safe(validated_url)})
    return render(request, 'cal/personal_added_event.html',{'event':event, 'valid_url':mark_safe(validated_url)})

#applies a django filter based on the GET request containing it and the list of events to apply it to
def apply_filter(events, request):
    eventfilter = EventFilter(request, queryset=events)
    events = eventfilter.qs
    return events, eventfilter

#View for showing event calendar events in List View
class EventListView(LoginRequiredMixin,generic.ListView):
    login_url = 'login'
    model = Event
    template_name = 'cal/eventlist.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        events = Event.objects.all().order_by('start_time')
        user = self.request.user
        if self.request.GET and "add_remove" in self.request.GET:
            event_ids = self.request.GET.getlist('add_remove_event')
            for event in Event.objects.all():
                if str(event.pk) in event_ids and event not in user.events_attending.all():
                    add_event_to_user(self.request, event.pk)
                    event_ids.remove(str(event.pk))
            for event in user.events_attending.all():  
                if str(event.pk) in event_ids:
                    remove_event_from_user(self.request, event.pk)
                    print("run")
        filtered_events, eventfilter = apply_filter(events, self.request.GET)
        eventlist = EventList(filtered_events)
        html_list = eventlist.format_table(filtered_events, user)
        context['eventlist'] = mark_safe(html_list)
        context['eventfilter'] = eventfilter.form
        return context

#View for showing event calendar events in List View
class PersonalListView(LoginRequiredMixin,generic.ListView):
    login_url = 'login'
    model = Event
    template_name = 'cal/personallist.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        if self.request.GET and "Remove" in self.request.GET:
            event_ids = self.request.GET.getlist('remove_event')
            for event in user.events_attending.all():  
                if str(event.pk) in event_ids:
                    remove_event_from_user(self.request, event.pk)
        events = user.events_attending.all().order_by('start_time')
        filtered_events, eventfilter = apply_filter(events, self.request.GET)
        eventlist = PersonalList(filtered_events)
        html_list = eventlist.format_table(filtered_events, user)
        context['personallist'] = mark_safe(html_list)
        context['eventfilter'] = eventfilter.form
        return context

