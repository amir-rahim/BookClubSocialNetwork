# Generated by Django 3.2.12 on 2022-02-22 17:25

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('BookClub', '0006_auto_20220222_1657'),
    ]

    operations = [
        migrations.CreateModel(
            name='BookReview',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rating', models.IntegerField(choices=[(0, 0), (1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7), (8, 8), (9, 9), (10, 10)], default=0, verbose_name='Ratings')),
                ('review', models.CharField(blank=True, max_length=1024, verbose_name='Review:')),
                ('createdOn', models.DateTimeField(auto_now=True, verbose_name='Reviewed on:')),
                ('book', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='BookClub.book')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('book', 'user')},
            },
        ),
    ]