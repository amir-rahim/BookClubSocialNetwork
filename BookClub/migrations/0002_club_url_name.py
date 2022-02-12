# Generated by Django 3.2.11 on 2022-02-10 13:08

import django.core.validators
from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('BookClub', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='club',
            name='url_name',
            field=models.CharField(default=django.utils.timezone.now, max_length=100, unique=True, validators=[django.core.validators.RegexValidator(code='invalid_url_name', message='Can only contain A-Z, a-z and 0-9 characters.', regex='[A-Za-z0-9]+')]),
            preserve_default=False,
        ),
    ]
