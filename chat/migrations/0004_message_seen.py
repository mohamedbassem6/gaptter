# Generated by Django 4.2.3 on 2023-09-05 22:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0003_remove_conversation_messages_message_conversation'),
    ]

    operations = [
        migrations.AddField(
            model_name='message',
            name='seen',
            field=models.BooleanField(default=False),
        ),
    ]
