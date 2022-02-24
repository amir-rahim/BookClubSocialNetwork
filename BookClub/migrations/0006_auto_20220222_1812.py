# Generated by Django 3.2.11 on 2022-02-22 18:12

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('BookClub', '0005_rename_url_name_club_club_url_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='booklist',
            name='books',
            field=models.ManyToManyField(to='BookClub.Book'),
        ),
        migrations.AlterField(
            model_name='meeting',
            name='book',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='BookClub.book'),
        ),
    ]
