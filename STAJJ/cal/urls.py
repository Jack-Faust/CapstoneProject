# vary from tutorial because it used outdated django
from django.urls import re_path
from . import views

app_name = 'cal'

urlpatterns = [
        re_path(r'^personalcal/listview/$', views.PersonalListView.as_view(), name='cockycal-personallist'),
    re_path(r'^eventcal/$', views.EventCalendarView.as_view(), name='cockycal-eventcal'),
    re_path(r'^personalcal/$', views.PersonalCalendarView.as_view(), name='cockycal-personalcal'),
    re_path(r'^eventcal/event/new/$', views.event, name='event_new'),
    re_path(r'^personalcal/event/new/$', views.pers_event, name='personal_event_new'),
    re_path(r'^event/edit/(?P<event_id>\d+)/$', views.event, name='event_edit'),
    re_path(r'^personalevent/edit/(?P<event_id>\d+)/$', views.pers_event, name='personal_event_edit'),
    re_path(r'^eventcal/event/details/(?P<event_id>\d+)/$', views.event_details, name='event_details'),
    re_path(r'^eventcal/event/added/(?P<event_id>\d+)/$', views.event_details, name='added_event'),
    re_path(r'^eventcal/listview/$', views.EventListView.as_view(), name='cockycal-eventlist'),
    re_path(r'^personalcal/event/details/(?P<event_id>\d+)/$', views.personal_event_details, name='personal_event_details'),
    re_path(r'^personalcal/event/added/(?P<event_id>\d+)/$', views.personal_event_details, name='personal_added_event'),
]