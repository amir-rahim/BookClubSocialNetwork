from django.conf import settings
import django.contrib.auth.models
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Book',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.TextField()),
                ('ISBN', models.CharField(max_length=15, unique=True)),
                ('author', models.TextField(max_length=100)),
                ('publicationYear', models.DateField()),
                ('publisher', models.TextField()),
                ('imageS', models.URLField(blank=True)),
                ('imageM', models.URLField(blank=True)),
                ('imageL', models.URLField(blank=True)),
            ],
            options={
                'ordering': ['-id'],
            },
        ),
        migrations.CreateModel(
            name='BookReview',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rating', models.IntegerField(auto_created=True, default=0)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('title', models.CharField(max_length=30)),
                ('content', models.CharField(max_length=1024)),
                ('slug', models.SlugField(max_length=30)),
                ('book_rating', models.IntegerField(choices=[(0, 0), (1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7), (8, 8), (9, 9), (10, 10)], default=0, verbose_name='Rating')),
                ('book', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='BookClub.book')),
            ],
        ),
        migrations.CreateModel(
            name='Club',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('club_url_name', models.CharField(max_length=100, unique=True, validators=[django.core.validators.RegexValidator(code='invalid_url_name', message='Can contain A-Z, a-z and 0-9 and underscores characters only.', regex='^[a-zA-Z0-9_]+$')])),
                ('description', models.CharField(max_length=250)),
                ('tagline', models.CharField(blank=True, max_length=120)),
                ('rules', models.CharField(blank=True, max_length=200)),
                ('is_private', models.BooleanField(default=False)),
                ('created_on', models.DateField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Forum',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=30)),
                ('slug', models.SlugField(max_length=30)),
                ('associated_with', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='BookClub.club')),
            ],
            options={
                'unique_together': {('title', 'associated_with')},
            },
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('username', models.CharField(max_length=30, unique=True, validators=[django.core.validators.RegexValidator(code='invalid_username', message='Usernames may only contain lowercase characters and . _ - but not as the first or last character.', regex='^[^._][-a-zA-Z0-9._]*[^._]$')])),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('public_bio', models.CharField(max_length=250)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Vote',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('type', models.BooleanField(verbose_name='Vote type')),
                ('object_id', models.PositiveIntegerField()),
                ('content_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contenttypes.contenttype')),
                ('creator', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('creator', 'object_id', 'content_type')},
            },
        ),
        migrations.CreateModel(
            name='Poll',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=120)),
                ('created_on', models.DateTimeField(auto_now=True)),
                ('deadline', models.DateTimeField(blank=True, null=True)),
                ('active', models.BooleanField(default=True)),
                ('club', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='BookClub.club')),
            ],
        ),
        migrations.CreateModel(
            name='Option',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.CharField(max_length=120)),
                ('book', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='BookClub.book')),
                ('poll', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='BookClub.poll')),
                ('voted_by', models.ManyToManyField(related_name='voters', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Meeting',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('meeting_time', models.DateTimeField()),
                ('created_on', models.DateField(auto_now_add=True)),
                ('location', models.CharField(blank=True, max_length=120)),
                ('title', models.CharField(max_length=120)),
                ('description', models.CharField(max_length=250)),
                ('type', models.CharField(choices=[('B', 'Book'), ('C', 'Club'), ('S', 'Social'), ('O', 'Other')], max_length=1)),
                ('book', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='BookClub.book')),
                ('club', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='BookClub.club')),
                ('members', models.ManyToManyField(related_name='meeting_attendees', to=settings.AUTH_USER_MODEL)),
                ('organiser', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='meeting_organiser', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='ForumPost',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rating', models.IntegerField(auto_created=True, default=0)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('title', models.CharField(max_length=30)),
                ('content', models.CharField(max_length=1024)),
                ('slug', models.SlugField(max_length=30)),
                ('creator', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('forum', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='BookClub.forum')),
                ('votes', models.ManyToManyField(blank=True, to='BookClub.Vote')),
            ],
            options={
                'ordering': ['-created_on'],
            },
        ),
        migrations.CreateModel(
            name='ForumComment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rating', models.IntegerField(auto_created=True, default=0)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('content', models.CharField(max_length=240)),
                ('creator', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('post', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='BookClub.forumpost')),
                ('votes', models.ManyToManyField(blank=True, to='BookClub.Vote')),
            ],
            options={
                'ordering': ['-created_on'],
            },
        ),
        migrations.CreateModel(
            name='ClubMembership',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('membership', models.IntegerField(choices=[(-1, 'Applicant'), (0, 'Member'), (1, 'Moderator'), (2, 'Owner')], default=-1)),
                ('joined_on', models.DateField(auto_now_add=True)),
                ('club', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='BookClub.club')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='BookReviewComment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rating', models.IntegerField(auto_created=True, default=0)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('content', models.CharField(max_length=240)),
                ('book_review', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='BookClub.bookreview')),
                ('creator', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('votes', models.ManyToManyField(blank=True, to='BookClub.Vote')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='bookreview',
            name='creator',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='bookreview',
            name='votes',
            field=models.ManyToManyField(blank=True, to='BookClub.Vote'),
        ),
        migrations.CreateModel(
            name='BookList',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('title', models.CharField(max_length=120)),
                ('description', models.CharField(blank=True, max_length=240)),
                ('books', models.ManyToManyField(blank=True, to='BookClub.Book')),
                ('creator', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddConstraint(
            model_name='clubmembership',
            constraint=models.UniqueConstraint(fields=('user', 'club'), name='unique_member'),
        ),
        migrations.AlterUniqueTogether(
            name='bookreview',
            unique_together={('book', 'creator')},
        ),
    ]
