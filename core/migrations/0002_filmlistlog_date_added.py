# Generated by Django 4.2.3 on 2023-09-13 18:15

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='filmlistlog',
            name='date_added',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]