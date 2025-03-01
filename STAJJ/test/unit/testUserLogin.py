from audioop import reverse
from django.test import TestCase
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.urls import reverse

class loginTestCase(TestCase):
    def setUp(self):
        user = User.objects.create(username='testuser', password='user123')
        User.save(user)
        
    def testUserLogin(self):
        user = authenticate(request=None, username='testuser', password='user123')
        