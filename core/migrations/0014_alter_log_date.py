# Generated by Django 4.2.3 on 2023-09-27 09:00

import datetime
import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0013_alter_log_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='log',
            name='date',
            field=models.DateField(default=datetime.date.today, validators=[django.core.validators.MaxValueValidator(datetime.date(2023, 9, 27), message='You have entered a date that is beyond the current timeline. Please check your flux capacitor and try again.')]),
        ),
    ]
