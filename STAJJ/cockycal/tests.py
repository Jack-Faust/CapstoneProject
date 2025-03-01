from django.test import TestCase
from django.utils import timezone
from cockycal.models import Post, CustomUser
from django.test import TestCase,RequestFactory
from .models import Image, TaskItem
from cal.models import Event
from users.models import CustomUser
from .views import home, profile, ItemCreate, ItemUpdate
from datetime import timedelta
from django.utils import timezone
from django.test import TestCase, Client
from django.urls import reverse
from .models import CustomUser, TaskItem
from .forms import ItemForm

# Create your tests here.
class HomePageTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.custom_user = CustomUser(username='utestuser')
        self.custom_user.set_password('testpassword')
        self.custom_user.save()
        # Create test events
        now = timezone.now()
        for i in range(7):
            event = Event(
                title=f'Test Event {i+1}',
                start_time=now + timedelta(days=i, hours=1),
                end_time=now + timedelta(days=i, hours=2),
            )
            event.save()
            
            self.custom_user.events_attending.add(event)
            if i < 5:
                self.custom_user.upcoming_events.add(event)
            task = TaskItem(title = f'Test Task{i+1}',
                            task_list = 'General Tasks',
                            due_date = '2022-01-01 05:00:00+00:00',
                            author = self.custom_user)
            task.save()
            
        self.custom_user.save()

    def test_fetch_weather_data(self):
        request = self.factory.get('/')
        request.user = self.custom_user
        response = home(request)
        weather_forecast = response.context_data['weather_forecast']
        self.assertIsNotNone(weather_forecast)
        self.assertEqual(len(weather_forecast), 7)

    def test_upcoming_events(self):
        request = self.factory.get('/')
        request.user = self.custom_user
        response = home(request)
        upcoming= response.context_data['upcoming']
        self.assertIsNotNone(upcoming)
        self.assertEqual(len(upcoming), 5)

    

class ProfilePageTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.custom_user = CustomUser(username='testuser')
        self.custom_user.set_password('testpassword')
        self.custom_user.save()
        now = timezone.now()
        for i in range(7):
            event = Event(
                title=f'Test Event {i+1}',
                start_time=now + timedelta(days=i, hours=1),
                end_time=now + timedelta(days=i, hours=2),
            )
            event.save()
            self.custom_user.events_attending.add(event)

        self.custom_user.save()

    def test_weekly_events(self):
        request = self.factory.get('/profile')
        request.user = self.custom_user
        response = profile(request)
        weekly= response.context_data['weekly']
        self.assertIsNotNone(weekly)
        self.assertEqual(len(weekly), 7)

# Unit test for ItemListView
class ItemListViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = CustomUser.objects.create_user(
            username='testuser', password='password')
        self.task1 = TaskItem.objects.create(
            author=self.user, title='Task 1', task_list='General Tasks')
        self.task2 = TaskItem.objects.create(
            author=self.user, title='Task 2', task_list='Priority Tasks')
        self.task3 = TaskItem.objects.create(
            author=self.user, title='Task 3', task_list='Class Tasks')
        self.task4 = TaskItem.objects.create(
            author=self.user, title='Task 4', task_list='Misc. Tasks')

    def test_item_list_view(self):
        self.client.login(username='testuser', password='password')
        url = reverse('cockycal-tasklist')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'cockycal/tasklist.html')
        self.assertContains(response, self.task1.title)
        self.assertContains(response, self.task2.title)
        self.assertContains(response, self.task3.title)
        self.assertContains(response, self.task4.title)
        self.assertEqual(len(response.context['object_list']), 4)
        self.assertEqual(
            response.context['general_tasks'][0].title, self.task1.title)
        self.assertEqual(
            response.context['pri_tasks'][0].title, self.task2.title)
        self.assertEqual(
            response.context['class_tasks'][0].title, self.task3.title)
        self.assertEqual(
            response.context['misc_tasks'][0].title, self.task4.title)

# Unit test for ItemCreate
class ItemCreateTestCase(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username='testuser', password='testpass'
        )

    def test_create_item(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.post(
            reverse('item-add'),
            data={
                'title': 'Test Task',
                'task_list': 'General Tasks',
                'due_date': '2022-01-01 05:00:00+00:00'
            }
        )

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('cockycal-tasklist'))

        task = TaskItem.objects.get(title='Test Task')
        self.assertEqual(task.author, self.user)
        self.assertEqual(task.task_list, 'General Tasks')
        self.assertEqual(str(task.due_date), '2022-01-01 05:00:00+00:00')

    def test_create_item_form(self):
        form_data = {
            'title': 'Test Task',
            'task_list': 'General Tasks',
            'due_date': '2022-01-01 05:00:00+00:00'
        }

        form = ItemForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_create_item_context(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('item-add'))
        form = response.context_data['form']
        self.assertIsInstance(form, ItemForm)
        self.assertEqual(response.context_data['title'], 'Create A New Task')
        self.assertEqual(response.status_code, 200)


# Unit test for ItemUpdate
class ItemUpdateTestCase(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username='testuser', password='testpass'
        )
        self.task = TaskItem.objects.create(
            title='Test Task',
            task_list='General Tasks',
            author=self.user,
            due_date='2022-01-01 05:00:00+00:00'
        )

    def test_update_item(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.post(
            reverse('item-update', args=[self.task.pk]),
            data={
                'title': 'Updated Test Task',
                'task_list': 'Priority Tasks',
                'due_date': '2022-02-01 05:00:00+00:00'
            }
        )

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('cockycal-tasklist'))

        updated_task = TaskItem.objects.get(pk=self.task.pk)
        self.assertEqual(updated_task.title, 'Updated Test Task')
        self.assertEqual(updated_task.task_list, 'Priority Tasks')
        self.assertEqual(str(updated_task.due_date), '2022-02-01 05:00:00+00:00')

    def test_update_item_form(self):
        form_data = {
            'title': 'Test Task',
            'task_list': 'General Tasks',
            'due_date': '2022-01-01 00:00:00'
        }

        form = ItemForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_update_item_context(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('item-update', args=[self.task.pk]))
        form = response.context_data['form']
        self.assertIsInstance(form, ItemForm)
        self.assertEqual(response.context_data['task_list'], 'General Tasks')
        self.assertEqual(response.context_data['title'], 'Edit Task')
        self.assertEqual(response.status_code, 200)

    def test_update_item_context_with_form(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('item-update', args=[self.task.pk]))
        form = response.context_data['form']
        self.assertIsInstance(form, ItemForm)
        self.assertEqual(response.context_data['task_list'], 'General Tasks')
        self.assertEqual(response.context_data['title'], 'Edit Task')
        self.assertEqual(response.status_code, 200)

# Unit test for ItemDelete
class ItemDeleteTestCase(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(username='testuser', password='testpass')
        self.task = TaskItem.objects.create(title='Test Task', author=self.user)

    def test_delete_item(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.post(reverse('item-delete', args=[self.task.pk]))
        self.assertRedirects(response, reverse('cockycal-tasklist'))
        self.assertFalse(TaskItem.objects.filter(title='Test Task').exists())


#tests for making a post 
class PostModelTest(TestCase):
    
    @classmethod
    #set up a test post 
    def setUpTestData(cls):
        author = CustomUser.objects.create(username='testuser')
        Post.objects.create(title='Test Post', content='Test Content', author=author)

    #tests that the length of the title does not exceed max length
    def test_title_max_length(self):
        post = Post.objects.get(id=1)
        max_length = post._meta.get_field('title').max_length
        self.assertEqual(max_length, 100)

    #testing that the posts contents matches the tests
    def test_post_contents(self):
        post = Post.objects.get(id=1)
        self.assertEqual(str(post), 'Test Post')
        
    #test that the date_posted field defaults to the current time when a new post is created
    def test_date(self):
        post = Post.objects.get(id=1)
        expected_value = timezone.now()
        actual_value = post.date_posted
        self.assertEqual(expected_value.date(), actual_value.date())
    
    #make sure author points to the correct user for a post 
    def test_author(self):
        post = Post.objects.get(id=1)
        author = CustomUser.objects.get(id=post.author.id)
        self.assertEqual(author.username, 'testuser')
        
    import datetime
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from .forms import ImageForm, ProfileUpdateForm, ItemForm, EditProfileForm
from .models import Image, TaskItem
from users.models import Profile


class ImageFormTestCase(TestCase):
    def setUp(self):
        self.image = SimpleUploadedFile(name='test_image.jpg', content=b'')
        self.form_data = {
            'title': 'Test Image',
            'image': self.image,
            'x': 0,
            'y': 0,
            'width': 100,
            'height': 100,
        }

    def test_image_form_valid(self):
        form = ImageForm(data=self.form_data)
        self.assertFalse(form.is_valid())

    def test_image_form_invalid(self):
        form_data = self.form_data.copy()
        form_data['image'] = None
        form = ImageForm(data=form_data)
        self.assertFalse(form.is_valid())


class ProfileUpdateFormTestCase(TestCase):
    def setUp(self):
        self.form_data = {
            'image': SimpleUploadedFile(name='test_image.jpg', content=b''),
        }

    def test_profile_update_form_valid(self):
        form = ProfileUpdateForm(data=self.form_data)
        self.assertTrue(form.is_valid())

    def test_profile_update_form_invalid(self):
        form_data = self.form_data.copy()
        form_data['image'] = None
        form = ProfileUpdateForm(data=form_data)
        self.assertTrue(form.is_valid())


