from django.db import models
from django.utils import timezone
from users.models import CustomUser
from django.urls import reverse
from django_resized import ResizedImageField

#https://www.youtube.com/watch?v=q4jPR-M0TAQ&list=PL-osiE80TeTtoQCKZ03TU5fNfx2UY6U4p&index=6 
# used this tutorial to set up my user registration system-->
# Create your models here.
def one_week_hence():
    return timezone.now() + timezone.timedelta(days=7)

# Profile Models
class Image(models.Model):
    title = models.CharField(max_length=200)
    image = ResizedImageField(size=[500, 500],null=True, blank=True, upload_to="images/")
    
    def clean_image(self):
        image_field = self.cleaned_data.get('image')
        if image_field:
            try:
                image_file = BytesIO(image_field.file.read())
                image = Image.open(image_file)
                image.thumbnail((300, 300), Image.ANTIALIAS)
                image_file = BytesIO()
                image.save(image_file, 'PNG')
                image_field.file = image_file
                image_field.image = image

                return image_field
            except IOError:
                logger.exception("Error during resize image")

class Post(models.Model):
    title = models.CharField(max_length=100)
    content = models.TextField()
    date_posted = models.DateTimeField(default=timezone.now)
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE)

    def __str__(self):
        return self.title

class TaskItem(models.Model):
    LISTS = (
        ('General Tasks','General Tasks'),
        ('Priority Tasks','Priority Tasks'),
        ('Class Tasks','Class Tasks'),
        ('Misc. Tasks','Misc. Tasks'),
    )
    title = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    created_date = models.DateTimeField(auto_now_add=True)
    due_date = models.DateTimeField(default=one_week_hence)
    task_list = models.CharField(max_length=100,choices=LISTS)
    # Jack LOOK HERE: this adds the author field
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    completed = models.BooleanField(default=False)

    def get_absolute_url(self):
        return reverse(
            "item-update", args=[str(self.task_list.id), str(self.id)]
        )
    def get_calendar_url(self):
        url = reverse(
            "item-update", args=[str(self.task_list.id), str(self.id)]
        )
        return f'<a href="{url}"> {self.title}</a>'

    def __str__(self):
        return f"{self.title}: due {self.due_date}"

    class Meta:
        ordering = ["due_date"]