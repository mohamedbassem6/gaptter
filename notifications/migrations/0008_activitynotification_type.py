# Generated by Django 4.2.3 on 2023-09-27 14:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notifications', '0007_activitynotification_reciever'),
    ]

    operations = [
        migrations.AddField(
            model_name='activitynotification',
            name='type',
            field=models.TextField(blank=True),
        ),
    ]
