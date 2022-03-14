# Generated by Django 3.2.12 on 2022-03-14 16:11

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('BookClub', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='forum',
            old_name='associatedWith',
            new_name='associated_with',
        ),
        migrations.AlterField(
            model_name='user',
            name='username',
            field=models.CharField(max_length=30, unique=True, validators=[django.core.validators.RegexValidator(code='invalid_username', message='Usernames may only contain lowercase characters and . _ - but not as the first or last character.', regex='^[^._][-a-zA-Z0-9._]*[^._]$')]),
        ),
        migrations.AlterUniqueTogether(
            name='forum',
            unique_together={('title', 'associated_with')},
        ),
    ]
