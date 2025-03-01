from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta

from .models import Event

class EventModelTest(TestCase):
    def setUp(self):
        self.event = Event.objects.create(
            title="Test Event",
            start_time=timezone.now(),
            end_time=timezone.now() + timedelta(hours=1),
            location="Test Location",
            description="Test Description",
            personal_event=False,
            posting_User_email="Test User",
            filterTag="UofSC Event"
        )

    def test_event_creation(self):
        self.assertTrue(isinstance(self.event, Event))

    def test_wrong_url(self):
        self.assertEqual(self.event.valid_url,self.event.description)

    def test_cal_urls(self):
        url = reverse('cal:event_details', args=(self.event.id,))
        self.assertTrue(self.event.title in self.event.get_html_url)
        self.assertTrue(url in self.event.get_html_url)
    
    def test_pers_cal_urls(self):
        url = reverse('cal:personal_event_details', args=(self.event.id,))
        self.assertTrue(self.event.title in self.event.get_personal_html_url)
        self.assertTrue(url in self.event.get_personal_html_url)

    def test_edit_cal_urls(self):
        url = reverse('cal:event_edit', args=(self.event.id,))
        self.assertTrue(self.event.title in self.event.get_edit_html_url)
        self.assertTrue(url in self.event.get_edit_html_url)

    def test_personal_edit_cal_urls(self):
        url = reverse('cal:personal_event_edit', args=(self.event.id,))
        self.assertTrue(self.event.title in self.event.get_personal_edit_html_url)
        self.assertTrue(url in self.event.get_personal_edit_html_url)

    def test_list_urls(self):
        url = reverse('cal:event_details', args=(self.event.id,))
        self.assertTrue(self.event.title in self.event.get_list_url)
        self.assertTrue(url in self.event.get_list_url)
    
    def test_pers_list_urls(self):
        url = reverse('cal:personal_event_details', args=(self.event.id,))
        self.assertTrue(self.event.title in self.event.get_personal_list_url)
        self.assertTrue(url in self.event.get_personal_html_url)

    def test_personal_edit_cal_urls(self):
        url = reverse('cal:personal_event_edit', args=(self.event.id,))
        self.assertTrue(self.event.title in self.event.get_personal_edit_html_url)
        self.assertTrue(url in self.event.get_personal_edit_html_url)