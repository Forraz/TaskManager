from .models import ProjectsModel, RoleUserProjectModel, FoldersModel, TasksModel, SubTasksModel, TagsModel, RoleModel
from django.core.exceptions import ObjectDoesNotExist
from graphql import GraphQLError


class IsAuthenticated:

    @classmethod
    def has_permission(cls, info, *args) -> None:
        if not info.context.request.user.is_authenticated:
            raise GraphQLError('Access is denied. The user is not authenticated.')


class IsNotAuthenticated:

    @classmethod
    def has_permission(cls, info, *args) -> None:
        if info.context.request.user.is_authenticated:
            raise GraphQLError('User already authenticated.')


class HasPermissionMixin:

    @classmethod
    def has_permission(cls, info):
        cls.set_objects(info)

        cls.user_has_permission(cls.user, cls.project)


class ProjectPermission(HasPermissionMixin):
    model = ProjectsModel

    @classmethod
    def set_objects(cls, info):
        cls.project = cls.model.objects.get(id=info.variable_values['id'])
        cls.user = info.context.request.user


class FolderPermission(HasPermissionMixin):
    model = FoldersModel

    @classmethod
    def set_objects(cls, info):
        folder = cls.model.objects.get(id=info.variable_values['id'])
        cls.project = folder.project.first()
        cls.user = info.context.request.user


class TaskPermission(HasPermissionMixin):
    model = TasksModel

    @classmethod
    def set_objects(cls, info):
        task = cls.model.objects.get(id=info.variable_values['id'])
        folder = task.folder.first()
        cls.project = folder.project.first()
        cls.user = info.context.request.user


class SubTaskPermission(HasPermissionMixin):
    model = SubTasksModel

    @classmethod
    def set_objects(cls, info):
        subtask = cls.model.objects.get(id=info.variable_values['id'])
        task = subtask.task.first()
        folder = task.folder.first()
        cls.project = folder.project.first()
        cls.user = info.context.request.user


class TagPermission(HasPermissionMixin):
    model = TagsModel

    @classmethod
    def set_objects(cls, info):
        cls.project = ProjectsModel.objects.get(id=info.variable_values['id'])
        cls.user = info.context.request.user


class RoleUserProjectPermission(HasPermissionMixin):
    model = RoleUserProjectModel

    @classmethod
    def set_objects(cls, info):
        cls.project = ProjectsModel.objects.get(id=info.variable_values['id'])
        cls.user = info.context.request.user


class RolePermission(HasPermissionMixin):
    model = RoleModel

    @classmethod
    def set_objects(cls, info):
        role = RoleModel.objects.get(id=info.variable_values['id'])
        cls.project = role.project.first()
        cls.user = info.context.request.user


class GetObjectPermissionMixin:

    @staticmethod
    def user_has_permission(user, project):

        try:
            if project.is_private:
                project.users.get(id=user.id)

        except ObjectDoesNotExist:
            raise GraphQLError('Access is denied.')


class AddObjectPermissionMixin:

    @staticmethod
    def user_has_permission(user, project):

        try:
            role = RoleUserProjectModel.objects.get(user=user.id, project=project).role

        except ObjectDoesNotExist:
            raise GraphQLError('Access is denied or object is not exist.')

        if not role.create:
            raise GraphQLError('Access is denied.')


class SetObjectPermissionMixin:

    @staticmethod
    def user_has_permission(user, project):

        try:
            role = RoleUserProjectModel.objects.get(user=user.id, project=project).role

        except ObjectDoesNotExist:
            raise GraphQLError('Access denied or object does not exist.')

        if not role.update:
            raise GraphQLError('Access denied.')


class RemoveObjectPermissionMixin:

    @staticmethod
    def user_has_permission(user, project):

        try:
            role = RoleUserProjectModel.objects.get(user=user.id, project=project).role

        except ObjectDoesNotExist:
            raise GraphQLError('Access is denied or object is not exist.')

        if not role.delete:
            raise GraphQLError('Access is denied.')


class RoleManagementPermissionMixin:

    @staticmethod
    def user_has_permission(user, project):

        try:
            role = RoleUserProjectModel.objects.get(user=user.id, project=project).role

        except ObjectDoesNotExist:
            raise GraphQLError('Access is denied or object is not exist.')

        if not role.role_management:
            raise GraphQLError('Access is denied.')


class UserManagementPermissionMixin:

    @staticmethod
    def user_has_permission(user, project):

        try:
            role = RoleUserProjectModel.objects.get(user=user.id, project=project.id).role

        except ObjectDoesNotExist:
            raise GraphQLError('Access is denied or object is not exist.')

        if not role.user_management:
            raise GraphQLError('Access is denied.')


class GetProjectPermission(GetObjectPermissionMixin, ProjectPermission):
    pass


class SetProjectPermission(SetObjectPermissionMixin, ProjectPermission):
    pass


class RemoveProjectPermission(RemoveObjectPermissionMixin, ProjectPermission):
    pass


class GetFolderPermission(GetObjectPermissionMixin, FolderPermission):
    pass


class AddFolderPermission(AddObjectPermissionMixin, FolderPermission):

    @classmethod
    def set_objects(cls, info):
        cls.project = ProjectsModel.objects.get(id=info.variable_values['id'])
        cls.user = info.context.request.user


class SetFolderPermission(SetObjectPermissionMixin, FolderPermission):
    pass


class RemoveFolderPermission(RemoveObjectPermissionMixin, FolderPermission):
    pass


class GetTaskPermission(GetObjectPermissionMixin, TaskPermission):
    pass


class AddTaskPermission(AddObjectPermissionMixin, TaskPermission):

    @classmethod
    def set_objects(cls, info):
        folder = FoldersModel.objects.get(id=info.variable_values['id'])
        cls.project = folder.project.first()
        cls.user = info.context.request.user


class SetTaskPermission(SetObjectPermissionMixin, TaskPermission):
    pass


class RemoveTaskPermission(RemoveObjectPermissionMixin, SubTaskPermission):
    pass


class GetSubTaskPermission(GetObjectPermissionMixin, SubTaskPermission):
    pass


class AddSubTaskPermission(AddObjectPermissionMixin, SubTaskPermission):

    @classmethod
    def set_objects(cls, info):
        task = TasksModel.objects.get(id=info.variable_values['id'])
        folder = task.folder.first()
        cls.project = folder.project.first()
        cls.user = info.context.request.user


class SetSubTaskPermission(SetObjectPermissionMixin, SubTaskPermission):
    pass


class RemoveSubTaskPermission(RemoveObjectPermissionMixin, SubTaskPermission):
    pass


class GetUserPermission(GetObjectPermissionMixin, RoleUserProjectPermission):
    pass


class UserManagementPermission(UserManagementPermissionMixin, RoleUserProjectPermission):
    pass


class RoleAssignmentPermission(RoleManagementPermissionMixin, RoleUserProjectPermission):
    pass


class GetTagPermission(GetObjectPermissionMixin, TagPermission):
    pass


class AddTagPermission(AddObjectPermissionMixin, TagPermission):
    pass


class SetTagPermission(SetObjectPermissionMixin, TagPermission):
    pass


class RemoveTagPermission(RemoveObjectPermissionMixin, TagPermission):
    pass


class GetRolePermission(GetObjectPermissionMixin, RolePermission):
    pass


class AddRolePermission(RoleManagementPermissionMixin, RolePermission):

    @classmethod
    def set_objects(cls, info):
        cls.project = ProjectsModel.objects.get(id=info.variable_values['id'])
        cls.user = info.context.request.user


class SetRolePermission(RoleManagementPermissionMixin, RolePermission):
    pass


class RemoveRolePermission(RoleManagementPermissionMixin, RolePermission):
    pass




