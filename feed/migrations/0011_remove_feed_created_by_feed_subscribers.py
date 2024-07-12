# Generated by Django 5.0.6 on 2024-07-09 18:13

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('feed', '0010_remove_waitlistrequest_invite_accepted_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RemoveField(
            model_name='feed',
            name='created_by',
        ),
        migrations.AddField(
            model_name='feed',
            name='subscribers',
            field=models.ManyToManyField(blank=True, to=settings.AUTH_USER_MODEL),
        ),
    ]