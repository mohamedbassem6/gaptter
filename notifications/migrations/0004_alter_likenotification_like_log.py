# Generated by Django 4.2.3 on 2023-09-27 09:01

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0014_alter_log_date'),
        ('notifications', '0003_remove_likenotification_gapt_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='likenotification',
            name='like_log',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.likelog'),
        ),
    ]
