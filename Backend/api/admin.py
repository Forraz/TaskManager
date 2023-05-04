from django.contrib import admin
from .models import ProjectsModel, FoldersModel, TasksModel, SubTasksModel


class ProjectsAdmin(admin.ModelAdmin):
    list_display = 'title', 'description', 'is_private',


class FoldersAdmin(admin.ModelAdmin):
    list_display = 'title', 'description'


class TasksAdmin(admin.ModelAdmin):
    list_display = 'title', 'description', 'is_finished',


class SubTasksAdmin(admin.ModelAdmin):
    list_display = 'title', 'description', 'is_finished',


admin.site.register(ProjectsModel, ProjectsAdmin)
admin.site.register(FoldersModel, FoldersAdmin)
admin.site.register(TasksModel, TasksAdmin)
admin.site.register(SubTasksModel, SubTasksAdmin)
