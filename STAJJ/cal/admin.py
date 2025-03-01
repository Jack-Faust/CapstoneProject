
# using tutorial, github found at https://github.com/huiwenhw/django-calendar
# also using tutorial found at: https://github.com/veryacademy/YT_Django_Admin_csv_Button_Upload/blob/main/core/urls.py

# Register your models here.
from django.contrib import admin
from .models import Event

from django.contrib import admin
from django.urls import path
from django.shortcuts import render
from django import forms
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse
import csv


def process_line(line):
    inQuotes = False
    fields=[]
    newfield=""
    for x in line:
        if x == "\"":
            if inQuotes == False:
                inQuotes=True
            elif inQuotes == True:
                inQuotes=False
        elif x == ",":
            if inQuotes == False:
                fields.append(newfield)
                newfield=""
            else:
                newfield+=x
        else:
            newfield+=x
    fields.append(newfield)
    return fields



class CsvImportForm(forms.Form):
    csv_upload = forms.FileField()

class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'location', 'start_time', 'end_time')

    def get_urls(self):
        urls = super().get_urls()
        new_urls = [path('upload-csv/', self.upload_csv),]
        return new_urls + urls

    def upload_csv(self, request):

        if request.method == "POST":
            csv_file = request.FILES["csv_upload"]
            
            if not csv_file.name.endswith('.csv'):
                messages.warning(request, 'The wrong file type was uploaded')
                return HttpResponseRedirect(request.path_info)
            
            file_data = csv_file.read().decode("utf-8")
            csv_data = file_data.split("\n")
            csv_data_iter = iter(csv_data)
            next(csv_data_iter)
            for line in csv_data_iter:
                fields = process_line(line)
                if len(fields)==7:
                    event_title = fields[1]
                    event_location = fields[2]
                    event_start_time = fields[3]
                    event_end_time = fields[4]
                    event_filter = fields[5]
                    event_url = fields[6]
                    try:
                        Event.objects.update_or_create(
                            title = event_title,
                            location = event_location,
                            start_time = event_start_time,
                            end_time = event_end_time,
                            filterTag = event_filter,
                            description = event_url
                        )
                    except: 
                        continue

            url = reverse('admin:index')
            return HttpResponseRedirect(url)

        form = CsvImportForm()
        data = {"form": form}
        return render(request, "admin/csv_upload.html", data)

admin.site.register(Event, EventAdmin)