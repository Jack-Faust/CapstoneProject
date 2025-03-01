from django.shortcuts import get_object_or_404
from .models import TaskItem
from users.models import CustomUser

class TaskItemUtil():
	
	def __init__(self, title):
		self.title = title

	#header as th (header of table)
	def format_header(self):
		title= '<th>Title</th>'
		header = title
		return f'<thead> <tr> {header} <tr> <thead>' 