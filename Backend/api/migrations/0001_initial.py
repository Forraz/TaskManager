# Generated by Django 4.2.1 on 2023-05-05 10:29

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone

admin_role = {
    'title': 'Administrator',
    '_create': 1,
    '_update': 1,
    '_delete': 1,
    'role_management': 1,
    'invite': 1,
    'user_management': 1,
    'is_admin': 1
}

user_role = {
    'title': 'User',
    '_create': 0,
    '_update': 0,
    '_delete': 0,
    'role_management': 0,
    'invite': 0,
    'user_management': 0,
    'is_admin': 0
}


def create_initial_data(apps, schema_editor):
    model = apps.get_model('api', 'RoleModel')
    initial_data = [
        model(**admin_role),
        model(**user_role),
    ]
    model.objects.bulk_create(initial_data)


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='FoldersModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=150)),
                ('description', models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='ProjectsModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=150)),
                ('description', models.TextField(blank=True, null=True)),
                ('is_private', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='RoleModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=50)),
                ('_create', models.BooleanField()),
                ('_update', models.BooleanField()),
                ('_delete', models.BooleanField()),
                ('role_management', models.BooleanField()),
                ('user_management', models.BooleanField()),
                ('is_admin', models.BooleanField()),
            ],
        ),
        migrations.CreateModel(
            name='SubTasksModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=150)),
                ('description', models.TextField(blank=True, null=True)),
                ('is_finished', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='TagsModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=50)),
                ('color', models.CharField(max_length=7)),
            ],
        ),
        migrations.CreateModel(
            name='TasksModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=150)),
                ('description', models.TextField(blank=True, null=True)),
                ('is_finished', models.BooleanField(default=False)),
                ('date_time', models.DateTimeField(default=None, null=True)),
                ('subtasks', models.ManyToManyField(related_name='task', to='api.subtasksmodel')),
                ('tags', models.ManyToManyField(related_name='task', to='api.tagsmodel')),
                ('users', models.ManyToManyField(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='RoleUserProjectModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.projectsmodel')),
                ('role', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.rolemodel')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='projectsmodel',
            name='default_role',
            field=models.ForeignKey(default=2, on_delete=django.db.models.deletion.SET_DEFAULT, to='api.rolemodel'),
        ),
        migrations.AddField(
            model_name='projectsmodel',
            name='folders',
            field=models.ManyToManyField(related_name='project', to='api.foldersmodel'),
        ),
        migrations.AddField(
            model_name='projectsmodel',
            name='roles',
            field=models.ManyToManyField(related_name='project', to='api.rolemodel'),
        ),
        migrations.AddField(
            model_name='projectsmodel',
            name='tags',
            field=models.ManyToManyField(related_name='project', to='api.tagsmodel'),
        ),
        migrations.AddField(
            model_name='projectsmodel',
            name='users',
            field=models.ManyToManyField(through='api.RoleUserProjectModel', to=settings.AUTH_USER_MODEL),
        ),
        migrations.CreateModel(
            name='NotificationsModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.TextField()),
                ('description', models.TextField()),
                ('date_time', models.DateTimeField(default=django.utils.timezone.now)),
                ('_from', models.CharField(max_length=100)),
                ('is_viewed', models.BooleanField(default=False)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='foldersmodel',
            name='tasks',
            field=models.ManyToManyField(related_name='folder', to='api.tasksmodel'),
        ),
        migrations.RunPython(create_initial_data)
    ]
