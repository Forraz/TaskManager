from django.db import models
from django.contrib.auth.models import User


class ProjectsModel(models.Model):
    """Модель для проектов """

    title = models.CharField(max_length=150)
    description = models.TextField(blank=True, null=True)
    users = models.ManyToManyField(User, through='RoleUserProjectModel')
    folders = models.ManyToManyField('FoldersModel', related_name='project')
    is_private = models.BooleanField(default=False)
    roles = models.ManyToManyField('RoleModel', related_name='project')
    default_role = models.ForeignKey('RoleModel', default=2, on_delete=
                                     models.SET_DEFAULT)
    tags = models.ManyToManyField('TagsModel', related_name='project')


class RoleModel(models.Model):
    """Модель для ролей"""

    title = models.CharField(max_length=50)
    _create = models.BooleanField()
    _update = models.BooleanField()
    _delete = models.BooleanField()
    role_management = models.BooleanField()
    user_management = models.BooleanField()


class RoleUserProjectModel(models.Model):
    """Модель для связи пользователей и ролей"""

    role = models.ForeignKey(RoleModel, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    project = models.ForeignKey(ProjectsModel, on_delete=models.CASCADE)


class FoldersModel(models.Model):
    """Модель для папок"""

    title = models.CharField(max_length=150)
    description = models.TextField(blank=True, null=True)
    tasks = models.ManyToManyField('TasksModel', related_name='folder')


class TasksModel(models.Model):
    """Модель для задач"""

    title = models.CharField(max_length=150)
    description = models.TextField(blank=True, null=True)
    is_finished = models.BooleanField(default=False)
    date = models.DateField(default=None, null=True)
    users = models.ManyToManyField(User)
    subtasks = models.ManyToManyField('SubTasksModel', related_name='task')
    tags = models.ManyToManyField('TagsModel', related_name='task')


class TagsModel(models.Model):
    """Модель для меток"""

    title = models.CharField(max_length=50)
    color = models.CharField(max_length=7)


class SubTasksModel(models.Model):
    """Модель для подзадач"""

    title = models.CharField(max_length=150)
    description = models.TextField(blank=True, null=True)
    is_finished = models.BooleanField(default=False)


class TokensModel(models.Model):

    refresh_token = models.TextField()





