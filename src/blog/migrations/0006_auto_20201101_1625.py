# Generated by Django 3.1.2 on 2020-11-01 15:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0005_auto_20201101_1556'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='article',
            options={'permissions': (('view_draft', 'Can view draft'), ('publish_draft', 'Can publish draft')), 'verbose_name': 'Artikel', 'verbose_name_plural': 'Artikel'},
        ),
    ]
