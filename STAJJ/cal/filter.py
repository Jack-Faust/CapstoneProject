import django_filters
from django_filters import CharFilter

from .models import Event

class EventFilter(django_filters.FilterSet):
    title = CharFilter(field_name="title", lookup_expr="icontains")
    location = CharFilter(field_name="location", lookup_expr="icontains")
    class Meta:
        model = Event
        fields = ["title", "location", "filterTag"]
