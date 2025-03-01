#code influenced from github tutorial for implementing a calendar 
# github found at https://github.com/huiwenhw/django-calendar
#additions and changes were made to that code to suit needs of our project
from django.shortcuts import get_object_or_404
from datetime import datetime, timedelta
from calendar import HTMLCalendar
from .models import Event
from .filter import EventFilter
from users.models import CustomUser
from cockycal.models import TaskItem
from django.utils import timezone


#Formats a table for the month called to show the events present in a calendar view
class EventCalendar(HTMLCalendar):

	def __init__(self, events, year=None, month=None):
		self.year = year
		self.month = month
		self.events = events
		super(EventCalendar, self).__init__()

	# formats a day as a td (cell element of a table)
	# filter events by day
	def formatday(self, day, events, user):
		current_tz = timezone.get_current_timezone()
		events_per_day = events.filter(start_time__day=day)
		d = ''
		events_continued=[]
		for event in events:
			if day > event.start_time.astimezone(current_tz).day and day <= event.end_time.astimezone(current_tz).day and event.start_time.astimezone(current_tz).day != event.end_time.astimezone(current_tz).day:
				events_continued.append(event)

		for event in events_per_day:
			if user.email == event.posting_User_email:
				if event.filterTag == "UofSC Event":
					d += f'<li class="uofsc"> {event.get_edit_html_url} </li>'
				elif event.filterTag == "Columbia Event":
					d += f'<li class="columbia"> {event.get_edit_html_url} </li>'
				elif event.filterTag == "Athletic Event":
					d += f'<li class="athletic"> {event.get_edit_html_url} </li>'
				elif event.filterTag == "Club Event":
					d += f'<li class="club"> {event.get_edit_html_url} </li>'
				elif event.filterTag == "Miscellaneous":
					d += f'<li class="misc"> {event.get_edit_html_url} </li>'
			else:
				if event.filterTag == "UofSC Event":
					d += f'<li class="uofsc"> {event.get_html_url} </li>'
				elif event.filterTag == "Columbia Event":
					d += f'<li class="columbia"> {event.get_html_url} </li>'
				elif event.filterTag == "Athletic Event":
					d += f'<li class="athletic"> {event.get_html_url} </li>'
				elif event.filterTag == "Club Event":
					d += f'<li class="club"> {event.get_html_url} </li>'
				elif event.filterTag == "Miscellaneous":
					d += f'<li class="misc"> {event.get_html_url} </li>'
		
		if len(events_continued) >0:
			d += '<li><b>Events Continued from Previous day:</b></li>'
			for event in events_continued:
				if user.email == event.posting_User_email:
					if event.filterTag == "UofSC Event":
						d += f'<li class="uofscindent"> {event.get_edit_list_url} </li>'
					elif event.filterTag == "Columbia Event":
						d += f'<li class="columbiaindent"> {event.get_edit_list_url} </li>'
					elif event.filterTag == "Athletic Event":
						d += f'<li class="athleticindent"> {event.get_edit_list_url} </li>'
					elif event.filterTag == "Club Event":
						d += f'<li class="clubindent"> {event.get_edit_list_url} </li>'
					elif event.filterTag == "Miscellaneous":
						d += f'<li class="miscindent"> {event.get_edit_list_url} </li>'
				else:
					if event.filterTag == "UofSC Event":
						d += f'<li class="uofscindent"> {event.get_list_url} </li>'
					elif event.filterTag == "Columbia Event":
						d += f'<li class="columbiaindent"> {event.get_list_url} </li>'
					elif event.filterTag == "Athletic Event":
						d += f'<li class="athleticindent"> {event.get_list_url} </li>'
					elif event.filterTag == "Club Event":
						d += f'<li class="clubindent"> {event.get_list_url} </li>'
					elif event.filterTag == "Miscellaneous":
						d += f'<li class="miscindent"> {event.get_list_url} </li>'
		if day != 0:
			return f"<td>{day}<div class=scrollable><span class='date'></span><ul> {d} </ul></div</td>"
		return '<td></td>'

	# formats a week as a tr (row element of a table)
	def formatweek(self, theweek, events, user):
		week = ''
		for d, weekday in theweek:
			week += self.formatday(d, events, user)
		return f'<tr> {week} </tr>'

	# formats a month as a table
	# filter events by year and month
	def formatmonth(self, user, eventlist, withyear=True):
		events = eventlist.filter(start_time__year=self.year, start_time__month=self.month, personal_event=False)

		cal = '<table border="0" cellpadding="0" cellspacing="0" class="calendar">\n'
		cal += f'{self.formatmonthname(self.year, self.month, withyear=withyear)}\n'
		cal += f'{self.formatweekheader()}\n'
		for week in self.monthdays2calendar(self.year, self.month):
			cal += f'{self.formatweek(week, events, user)}\n'
		return cal

	#Displays the Legend for the event calendar
	def legend(self):
		view = '<table border="0" cellpadding="0" cellspacing="0" class="legend">\n'
		header = '<th class="legend"> Legend </th>'
		tags = ['UofSC Event', 'Columbia Event', 'Athletic Event', 'Club Event', 'Miscellaneous']
		info = ""
		for tag in tags:
			if tag == "UofSC Event":
				info += f'<li class="uofsc"> {tag} </li>'
			elif tag == "Columbia Event":
				info += f'<li class="columbia"> {tag} </li>'
			elif tag == "Athletic Event":
				info += f'<li class="athletic"> {tag} </li>'
			elif tag == "Club Event":
				info  += f'<li class="club"> {tag}</li>'
			elif tag == "Miscellaneous":
				info += f'<li class="misc"> {tag} </li>'
		cell = f'<td class="legend">{info}</td>'
		row = f'<tr class="legend">{cell}</tr>'
		view += header + row
		return view


#Formats a table for the month called to show the personal events present in a calendar view
class PersonalCalendar(HTMLCalendar):

	def __init__(self, events,year=None, month=None):
		self.year = year
		self.month = month
		super(PersonalCalendar, self).__init__()

	# formats a day as a td (cell element of a table)
	# filter events by day
	def formatday(self, day, personal_events, tasks_list, user):
		current_tz = timezone.get_current_timezone()
		personal_events_per_day = personal_events.filter(start_time__day=day)
		tasks_list_per_day =  tasks_list.filter(due_date__day=day)
		d = ''
		events_continued=[]
		for event in personal_events:
			if day > event.start_time.astimezone(current_tz).day and day <= event.end_time.astimezone(current_tz).day and event.start_time.astimezone(current_tz).day != event.end_time.astimezone(current_tz).day:
				events_continued.append(event)
		for pers_event in personal_events_per_day:
			if user.email == pers_event.posting_User_email:
					if pers_event.filterTag == "UofSC Event":
						d += f'<li class="uofsc"> {pers_event.get_personal_edit_html_url} </li>'
					elif pers_event.filterTag == "Columbia Event":
						d += f'<li class="columbia"> {pers_event.get_personal_edit_html_url} </li>'
					elif pers_event.filterTag == "Athletic Event":
						d += f'<li class="athletic"> {pers_event.get_personal_edit_html_url} </li>'
					elif pers_event.filterTag == "Club Event":
						d += f'<li class="club"> {pers_event.get_personal_edit_html_url} </li>'
					elif pers_event.filterTag == "Miscellaneous":
						d += f'<li class="misc"> {pers_event.get_personal_edit_html_url} </li>'
			else:
				if pers_event.personal_event == False:
					if pers_event.filterTag == "UofSC Event":
						d += f'<li class="uofsc"> {pers_event.get_personal_html_url} </li>'
					elif pers_event.filterTag == "Columbia Event":
						d += f'<li class="columbia"> {pers_event.get_personal_html_url} </li>'
					elif pers_event.filterTag == "Athletic Event":
						d += f'<li class="athletic"> {pers_event.get_personal_html_url} </li>'
					elif pers_event.filterTag == "Club Event":
						d += f'<li class="club"> {pers_event.get_personal_html_url} </li>'
					elif pers_event.filterTag == "Miscellaneous":
						d += f'<li class="misc"> {pers_event.get_personal_html_url} </li>'
		if len(events_continued) >0:
			d += '<li><b>Events Continued from Previous day:</b></li>'
			for event in events_continued:
				if user.email == event.posting_User_email:
					if event.filterTag == "UofSC Event":
						d += f'<li class="uofscindent"> {event.get_personal_edit_list_url} </li>'
					elif event.filterTag == "Columbia Event":
						d += f'<li class="columbiaindent"> {event.get_personal_edit_list_url} </li>'
					elif event.filterTag == "Athletic Event":
						d += f'<li class="athleticindent"> {event.get_personal_edit_list_url} </li>'
					elif event.filterTag == "Club Event":
						d += f'<li class="clubindent"> {event.get_personal_edit_list_url}</li>'
					elif event.filterTag == "Miscellaneous":
						d += f'<li class="miscindent"> {event.get_personal_edit_list_url} </li>'
				else:
					if event.filterTag == "UofSC Event":
						d += f'<li class="uofscindent"> {event.get_personal_list_url} </li>'
					elif event.filterTag == "Columbia Event":
						d += f'<li class="columbiaindent"> {event.get_personal_list_url} </li>'
					elif event.filterTag == "Athletic Event":
						d += f'<li class="athleticindent"> {event.get_personal_list_url}</li>'
					elif event.filterTag == "Club Event":
						d += f'<li class="clubindent"> {event.get_personal_list_url}</li>'
					elif event.filterTag == "Miscellaneous":
						d += f'<li class="miscindent"> {event.get_personal_list_url} </li>'
		if len(tasks_list_per_day) > 0:
			d += '<li><b class="tasks">Tasks due today:</b></li>' 
			for task_item in tasks_list_per_day:
				d += f'<li class="task">{task_item.title}</li>'
	
		if day != 0:
			return f"<td>{day}<div class=scrollable><span class='date'></span><ul> {d} </ul></div</td>"
		return '<td></td>'

	# formats a week as a tr (row element of a table)
	def formatweek(self, theweek, personal_events, tasks_list, user):
		week = ''
		for d, weekday in theweek:
			week += self.formatday(d, personal_events, tasks_list, user)
		return f'<tr> {week} </tr>'

	# formats a month as a table
	# filter events by year and month
	def formatmonth(self, user, events, tasks_list, withyear=True):
		events = events.filter(start_time__year=self.year, start_time__month=self.month)
		cal = '<table border="0" cellpadding="0" cellspacing="0" class="calendar">\n'
		cal += f'{self.formatmonthname(self.year, self.month, withyear=withyear)}\n'
		cal += f'{self.formatweekheader()}\n'
		tasks_list_per_month =  tasks_list.filter(due_date__month=self.month)
		for week in self.monthdays2calendar(self.year, self.month):
			cal += f'{self.formatweek(week, events, tasks_list_per_month,user)}\n'
		return cal
	
	#Displays the legend for the Personal Calendar
	def legend(self):
		view = '<table border="0" cellpadding="0" cellspacing="0" class="legend">\n'
		header = '<th class="legend"> Legend </th>'
		tags = ['UofSC Event', 'Columbia Event', 'Athletic Event', 'Club Event', 'Miscellaneous']
		info = ""
		for tag in tags:
			if tag == "UofSC Event":
				info += f'<li class="uofsc"> {tag} </li>'
			elif tag == "Columbia Event":
				info += f'<li class="columbia"> {tag} </li>'
			elif tag == "Athletic Event":
				info += f'<li class="athletic"> {tag} </li>'
			elif tag == "Club Event":
				info  += f'<li class="club"> {tag}</li>'
			elif tag == "Miscellaneous":
				info += f'<li class="misc"> {tag} </li>'
		cell = f'<td class="legend">{info}</td>'
		row = f'<tr class="legend">{cell}</tr>'
		view += header + row
		return view

#Formats List view of Event Calendar
class EventList():
	current_day = None
	last_printed_day = None

	def __init__(self, events):
		self.events = events

	#header as th (header of table)
	def format_header(self):
		title= '<th>Title</th>'
		location = '<th>Location</th>'
		start_time= '<th>Start Time</th>'
		end_time= '<th>End Time</th>'
		tag = '<th>Filter Tag</th>'
		remove_event = '<th>Remove Event</th>'
		add_event = '<th>Add Event</th>'
		header = title + location + start_time + end_time + tag + add_event + remove_event
		return f'<thead> <tr>{header} <tr> <thead>' 
	
	#event as tr (row of table) with variables as td (cell of table)
	def format_row(self, event, user):
		current_tz = timezone.get_current_timezone()
		if self.current_day != self.last_printed_day:
			print_day = f'<tr> <th> {event.start_time.strftime("%D")}</th> <tr>'
			self.last_printed_day = self.current_day
			return print_day + self.format_row(event, user)
		if user.email == event.posting_User_email:
			title= f'<td>{event.get_edit_list_url}</td>'
		else:
			title= f'<td>{event.get_list_url}</td>'
		location = f'<td>{event.location}</td>'
		start_time= f'<td>{event.start_time.astimezone(current_tz).strftime("%D  %H:%M")}</td>'
		end_time= f'<td>{event.end_time.astimezone(current_tz).strftime("%D  %H:%M")}</td>'
		tag = f'<td>{event.filterTag}</td>'
		add_remove_event =''
		if event in user.events_attending.all():
			add_remove_event = f'<td></td><td><input type = "checkbox" name="add_remove_event" value="{ event.id }"></td>'
		else: 
			add_remove_event = f'<td><input type = "checkbox" name="add_remove_event" value="{ event.id }"></td><td></td>'
		row = title + location + start_time + end_time + tag + add_remove_event
		return f'<tr> {row} <tr>' 

	#creates a row for every element in the list passed
	def format_table(self,  eventlist, user):
		events = eventlist.filter(personal_event=False)
		listview = '<table border="0" cellpadding="0" cellspacing="0" class="table">\n'
		listview += self.format_header()

		for event in events:
			self.current_day = event.start_time.day
			listview += self.format_row(event, user)
		return listview

#This class is used to format the event list for events added to a personal Calendar
class PersonalList():
	current_day = None
	last_printed_day = None

	def __init__(self, events):
		self.events = events

	#header as th (header of table)
	def format_header(self):
		title= '<th>Title</th>'
		location = '<th>Location</th>'
		start_time= '<th>Start Time</th>'
		end_time= '<th>End Time</th>'
		tag = '<th>Filter Tag</th>'
		remove_event = '<th>Remove Event</th>'
		header = title + location + start_time + end_time + tag +remove_event
		return f'<thead> <tr>{header} <tr> <thead>' 
	
	#event as tr (row of table) with variables as td (cell of table)
	#displays check boxs to remove events and has logic to show both task list events and events carried over from other days 
	def format_row(self, event, user):
		current_tz = timezone.get_current_timezone()
		if self.current_day != self.last_printed_day:
			print_day = f'<tr> <th> {event.start_time.strftime("%D")}</th> <tr>'
			self.last_printed_day = self.current_day
			return print_day + self.format_row(event, user)
		if user.email == event.posting_User_email:
			title= f'<td>{event.get_personal_edit_list_url}</td>'
		else:
			title= f'<td>{event.get_personal_list_url}</td>'
		location = f'<td>{event.location}</td>'
		start_time= f'<td>{event.start_time.astimezone(current_tz).strftime("%D  %H:%M")}</td>'
		end_time= f'<td>{event.end_time.astimezone(current_tz).strftime("%D  %H:%M")}</td>'
		tag = f'<td>{event.filterTag}</td>'
		remove_event = f'<td><input type = "checkbox" name="remove_event" value="{ event.id }"></td>'
		row = title + location + start_time + end_time + tag + remove_event
		return f'<tr> {row} <tr>' 

	#creates a row for every element in the list passed
	def format_table(self,  events, user):
		listview = '<table border="0" cellpadding="0" cellspacing="0" class="table">\n'
		listview += self.format_header()
		has_events = True
		if len(events) == 0:
			has_events = False
		if has_events == False:
			listview += '<tr><td><b>No Events Added to Personal Calendar at this time!</b></td></tr>'
		for event in events:
			self.current_day = event.start_time.day
			listview += self.format_row(event, user)
		return listview