# Generated by Django 3.1.2 on 2020-10-30 14:23

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0003_auto_20201030_1447'),
    ]

    operations = [
        migrations.AddField(
            model_name='tag',
            name='created',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
