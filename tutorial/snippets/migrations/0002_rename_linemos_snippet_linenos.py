# Generated by Django 4.1.4 on 2022-12-24 04:43

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('snippets', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='snippet',
            old_name='linemos',
            new_name='linenos',
        ),
    ]
