from django.contrib.auth.admin import UserAdmin
from .models import CustomUser
from django.contrib import admin
from .models import Profile

admin.site.register(Profile)
# Register your models here.
class CustomUserAdmin(UserAdmin):
    list_display = (
        'username','email','first_name','last_name','get_events_attending','get_upcoming_events'
    )
    def get_events_attending(self, obj):
        return ', '.join([str(event) for event in obj.events_attending.all()])

    get_events_attending.short_description = 'Events Attending'
    fieldsets=(
        (None,{ 'fields': ('username','password') } ),
        ('Personal info', {  'fields' : ('first_name','last_name','email') }),
        ('Permissions', {'fields':('is_superuser','groups','user_permissions') }),
        ('Events Attending',{'fields':('events_attending',) }),
    )
    def get_upcoming_events(self,obj):
        return ;', '.join([str(event) for event in obj.upcoming_events.all()])

    get_upcoming_events.short_description = 'Upcoming Events'
    fieldsets=(
        (None,{ 'fields': ('username','password') } ),
        ('Personal info', {  'fields' : ('first_name','last_name','email') }),
        ('Permissions', {'fields':('is_superuser','groups','user_permissions') }),
        ('Events Attending',{'fields':('events_attending',) }),
        ('Upcoming Events', {'fields':('upcoming_events',) }),
    )


admin.site.register(CustomUser, CustomUserAdmin)