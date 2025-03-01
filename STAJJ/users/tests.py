from audioop import reverse
from django.test import TestCase
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.urls import reverse
from users.models import Profile
from django.contrib.auth import get_user_model
from users.forms import ProfileUpdateForm
from users.forms import UserRegisterForm
from users.forms import UserUpdateForm
from users.models import CustomUser
from users.models import CustomUser, Event
from django.test import RequestFactory
from cal.models import Event
from .utils import add_event_to_user, remove_event_from_user
from django.utils import timezone
from datetime import timedelta    

        
#testing updating a profile form
class ProfileUpdateFormTest(TestCase):
    #tests profile form has valid inputs 
    def test_valid_form(self):
        data = {
            'image': 'image.jpg',
            'name': 'John Doe',
            'occupation': 'Developer',
            'birthday': '1990-01-01',
            'phonenumber': '+1234567890'
        }
        form = ProfileUpdateForm(data=data)
        self.assertFalse(form.is_valid())
        
    #tests profile form has invalid (null) inputs 
    def test_invalid_form(self):
        data = {
            'image': '',
            'name': '',
            'occupation': '',
            'birthday': '',
            'phonenumber': ''
        }
        form = ProfileUpdateForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertEqual(len(form.errors), 3)
        
#testing registering a new user 
class UserRegisterFormTest(TestCase):
    
    #tests that a user registers with correct credentials 
    #must be a usc email address
    def test_valid_form(self):
        data = {
            'username': 'testuser',
            'email': 'testuser@email.sc.edu',
            'password1': 'testpassword123',
            'password2': 'testpassword123'
        }
        form = UserRegisterForm(data=data)
        self.assertTrue(form.is_valid())

    #test that a user uses a usc email 
    def test_invalid_email(self):
        data = {
            'username': 'testuser',
            'email': 'testuser@gmail.com', #not USC email
            'password1': 'testpassword123',
            'password2': 'testpassword123'
        }
        form = UserRegisterForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertEqual(len(form.errors), 1)
        self.assertEqual(form.errors['email'], ['Must be a USC email address'])
        
      
#testing a user updating their profile   
class UserUpdateFormTest(TestCase):
    
    #create a fake user 
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username='testuser',
            email='testuser@email.sc.edu',
            password='testpassword123'
        )

    #tests that the user uses correct credentials when updating their username and email
    def test_valid_form(self):
        data = {
            'username': 'testuserupdated',
            'email': 'testuserupdated@email.sc.edu',
        }
        form = UserUpdateForm(data=data, instance=self.user)
        self.assertTrue(form.is_valid())
        form.save()
        self.assertEqual(self.user.username, 'testuserupdated')
        self.assertEqual(self.user.email, 'testuserupdated@email.sc.edu')

    #test for not valid credentials in user form 
    def test_invalid_form(self):
        data = {
            'username': '',
            'email': '',
        }
        form = UserUpdateForm(data=data, instance=self.user)
        self.assertFalse(form.is_valid())
        self.assertEqual(len(form.errors), 2)
        self.assertEqual(form.errors['username'], ['This field is required.'])
        self.assertEqual(form.errors['email'], ['This field is required.'])


class UtilsTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.custom_user = CustomUser(username='testuser')
        self.custom_user.set_password('testpassword')
        self.custom_user.save()
        now = timezone.now()
        for i in range(10):
            event = Event(
                title=f'Test Event {i+1}',
                start_time=now + timedelta(days=i, hours=1),
                end_time=now + timedelta(days=i, hours=2),
            )
            event.save()

    def test_add_event_to_user_upcoming_less_than_5(self):
        now = timezone.now()
        event = Event(
            title='Test Event',
            start_time=now + timedelta(days=1),
            end_time=now + timedelta(days=1, hours=1),
        )
        event.save()

        request = self.factory.get('/')
        request.user = self.custom_user
        add_event_to_user(request, event.pk)

        self.custom_user.refresh_from_db()
        self.assertIn(event, self.custom_user.upcoming_events.all())

    def test_add_event_to_user_upcoming_replace_latest(self):
        # Create 5 events and add them to the user
        now = timezone.now()
        for i in range(5):
            event = Event(
                title=f'Test Event {i+1}',
                start_time=now + timedelta(days=i+1,hours=1),
                end_time=now + timedelta(days=i+1, hours=2),
            )
            event.save()

            request = self.factory.get('/')
            request.user = self.custom_user
            add_event_to_user(request, event.pk)

        # Create a new event that starts before the last event
        new_event = Event(
            title='New Test Event',
            start_time=now + timedelta(days=4, hours=1),
            end_time=now + timedelta(days=4, hours=2),
        )
        new_event.save()

        request = self.factory.get('/')
        request.user = self.custom_user
        add_event_to_user(request, new_event.pk)

        self.custom_user.refresh_from_db()

        # Check if the new event was added to upcoming_events
        self.assertIn(new_event, self.custom_user.upcoming_events.all())

        # Check if the latest event was removed from upcoming_events
        latest_event = Event.objects.filter(title='Test Event 5')
        self.assertNotIn(latest_event, self.custom_user.upcoming_events.all())

    def test_remove_event_and_replace_with_next(self):
    # Create 5 events and add them to the user
        now = timezone.now()
        for i in range(5):
            event = Event(
                title=f'Test Event {i+1}',
                start_time=now + timedelta(days=i+1,hours=1),
                end_time=now + timedelta(days=i+1, hours=2),
            )
            event.save()

            request = self.factory.get('/')
            request.user = self.custom_user
            add_event_to_user(request, event.pk)

        # Create an additional event
        additional_event = Event(
            title='Additional Test Event',
            start_time=now + timedelta(days=6),
            end_time=now + timedelta(days=6, hours=1),
        )
        additional_event.save()

        request = self.factory.get('/')
        request.user = self.custom_user
        add_event_to_user(request, additional_event.pk)

        # Remove the first event
        first_event = Event.objects.filter(title='Test Event 1').order_by('start_time').first()
        request = self.factory.get('/')
        request.user = self.custom_user
        remove_event_from_user(request, first_event.pk)

        self.custom_user.refresh_from_db()

        # Check if the first event was removed from the upcoming_events
        self.assertNotIn(first_event, self.custom_user.upcoming_events.all())

        # Check if the additional event was added to the upcoming_events
        self.assertIn(additional_event, self.custom_user.upcoming_events.all())  
        
