# Generated by Django 4.1.7 on 2023-03-30 15:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cal', '0001_initial'),
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='upcoming_events',
            field=models.ManyToManyField(blank=True, related_name='upcoming_events', to='cal.event'),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='events_attending',
            field=models.ManyToManyField(blank=True, related_name='all_events', to='cal.event'),
        ),
    ]
