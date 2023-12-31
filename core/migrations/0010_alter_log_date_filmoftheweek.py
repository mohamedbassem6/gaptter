# Generated by Django 4.2.3 on 2023-09-18 16:16

import datetime
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0009_seengapt'),
    ]

    operations = [
        migrations.AlterField(
            model_name='log',
            name='date',
            field=models.DateField(default=datetime.date.today, validators=[django.core.validators.MaxValueValidator(datetime.date(2023, 9, 18), message='You have entered a date that is beyond the current timeline. Please check your flux capacitor and try again.')]),
        ),
        migrations.CreateModel(
            name='FilmOfTheWeek',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('duration', models.DurationField()),
                ('film', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.film')),
            ],
        ),
    ]
