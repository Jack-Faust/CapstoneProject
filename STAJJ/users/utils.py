from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from cal.models import Event
from .models import CustomUser
from django.utils import timezone
from datetime import datetime, timedelta
import requests
from cockycal.models import TaskItem

#adds events to a users events attending list 
def add_event_to_user(request,event_id):
    user = CustomUser.objects.get(pk=request.user.pk)
    event = get_object_or_404(Event,pk=event_id)
    event.hide = False
    event.save()
    #adds the event to users personal calendar
    user.events_attending.add(event)
    #if upcoming events has less than 5 events, add event to upcoming
    if len(user.upcoming_events.all()) < 5:
        user.upcoming_events.add(event)
    #if not, check if this event is before the last event
    else:
        for e in user.upcoming_events.all().order_by('start_time'):
            #if it is, remove the last event and put this event in.
            if event.start_time.date() >= timezone.now().date() and event.start_time.date() < e.start_time.date():
                last = user.upcoming_events.all().order_by('start_time').last()
                user.upcoming_events.remove(last)
                user.upcoming_events.add(event)
                break
    user.save()
    return HttpResponse("Event {} has been added to user {}'s events.".format(event.title, user.username))

#removes events from a users events attending list 
def remove_event_from_user(request,event_id):
    user = CustomUser.objects.get(pk=request.user.pk)
    event = get_object_or_404(Event,pk=event_id)
    #remove the event from personal calendar
    user.events_attending.remove(event)
    #if there is anything in upcoming events, remove the event
    if user.upcoming_events:
        user.upcoming_events.remove(event)
        #if theres more events in the personal calendar that are not in upcoming, add it to upcoming.
        for e in user.events_attending.all().order_by('start_time'):
            if e.start_time.date() >= timezone.now().date() and e not in user.upcoming_events.all():
                user.upcoming_events.add(e)
    user.save()
    return HttpResponse("Event {} has been removed from user {}'s events.".format(event.title, user.username))
 
#returns the upcoming events in order
def upcoming_events(user):
    events = []
    #gets current date and time
    current_date = timezone.localtime(timezone.now()).date()
    current_time = timezone.localtime(timezone.now()).time()
    #gets the time and date for each event in upcoming and sorts them
    for event in user.events_attending.all().order_by('start_time'):
       if len(events) < 5:
            event_date = timezone.localtime(event.start_time).date()
            event_time = timezone.localtime(event.start_time).time()
        

            if event_date > current_date:
                events.append(event)
            elif event_date == current_date and event_time >= current_time:
                events.append(event)

    return events

def upcoming_tasks(user):
    users_tasks = TaskItem.objects.filter(author=user).order_by('due_date')
    tasks = []
    #gets current date and time
    current_date = timezone.localtime(timezone.now()).date()
    #gets the time and date for each event in upcoming and sorts them
    for task in users_tasks:
        task_duedate = timezone.localtime(task.due_date).date()
       
        if task_duedate >= current_date and task.completed == False and len(tasks) < 10:
            tasks.append(task)

    return tasks

#gets the events for the next 7 days
def weekly_events(user): 
    events=[] 
    #for events in your personal calendar, add events that are between now and one week from now.      
    for event in user.events_attending.all().order_by('start_time'):
        if timezone.now().date() + timedelta(weeks=1)>= event.start_time.date() >= timezone.now().date():
            events.append(event)
    return events
    
