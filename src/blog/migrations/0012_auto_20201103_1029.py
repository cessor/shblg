# Generated by Django 3.1.2 on 2020-11-03 09:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0011_auto_20201103_0935'),
    ]

    operations = [
        migrations.AlterField(
            model_name='author',
            name='portrait',
            field=models.ImageField(blank=True, height_field='height', max_length=255, null=True, upload_to='portraits', verbose_name='Portait', width_field='width'),
        ),
    ]
