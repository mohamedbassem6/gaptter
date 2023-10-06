# Generated by Django 4.2.3 on 2023-09-29 15:36

import datetime
import django.core.validators
from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0015_alter_person_options'),
    ]

    operations = [
        migrations.AlterField(
            model_name='filmoftheweek',
            name='comment',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='filmoftheweek',
            name='end_date',
            field=models.DateTimeField(blank=True),
        ),
        migrations.AlterField(
            model_name='filmoftheweek',
            name='start_date',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AlterField(
            model_name='log',
            name='date',
            field=models.DateField(default=datetime.date.today, validators=[django.core.validators.MaxValueValidator(datetime.date(2023, 9, 29), message='You have entered a date that is beyond the current timeline. Please check your flux capacitor and try again.')]),
        ),
    ]
