import datetime
from typing import Optional, List

from django.db import transaction
from .permissions import *
from .models import ProjectsModel, FoldersModel, TasksModel, SubTasksModel, RoleModel, NotificationsModel
from django.contrib.auth.models import User
from my_jwt.jwt import AccessToken, RefreshToken, decode, encode, check_refresh_token
import strawberry
from .scheduler import schedule_task, scheduler


def get_info(info, id):
    info.variable_values['id'] = id

    return info


@strawberry.type
class TokensType:

    def __init__(self, access_token, refresh_token):
        self.access_token = access_token
        self.refresh_token = refresh_token

    access_token: str
    refresh_token: str


class CheckAccessMixin:

    @classmethod
    def check_access(cls, *args):
        for i in cls.permission_classes:
            i.has_permission(*args)


class ProjectResolver(CheckAccessMixin):
    model = ProjectsModel


class FolderResolver(CheckAccessMixin):
    model = FoldersModel
    parent = ProjectResolver


class TaskResolver(CheckAccessMixin):
    model = TasksModel
    parent = FolderResolver


class SubTaskResolver(CheckAccessMixin):
    model = SubTasksModel
    parent = TaskResolver


class RoleResolver(CheckAccessMixin):
    model = RoleModel


class RoleUserProjectResolver(CheckAccessMixin):
    model = RoleUserProjectModel


class TagResolver(CheckAccessMixin):
    model = TagsModel


class UserResolver(CheckAccessMixin):
    model = User


class NotificationResolver(CheckAccessMixin):
    model = NotificationsModel


class GetResolver:

    @classmethod
    def resolver(cls, info, id: int):
        info = get_info(info, id)
        cls.check_access(info)

        return cls.model.objects.get(id=id)


class RemoveResolver:

    @classmethod
    def resolver(cls, info, id: int):
        info = get_info(info, id)
        cls.check_access(info)

        cls.model.objects.get(id=id).delete()

        return True


class GetProjectResolver(ProjectResolver, GetResolver):
    permission_classes = [IsAuthenticated, GetProjectPermission]


class GetUserProjectsResolver(ProjectResolver):
    permission_classes = [IsAuthenticated]

    @classmethod
    def resolver(cls, info):
        cls.check_access(info)

        user = info.context.request.user

        return list(cls.model.objects.filter(users=user.id))


class AddProjectResolver(ProjectResolver):
    permission_classes = [IsAuthenticated]

    @classmethod
    @transaction.atomic()
    def resolver(cls, info, title: str, description: Optional[str] = None, is_private: Optional[bool] = True):
        cls.check_access(info)

        user = info.context.request.user.id

        project = cls.model.objects.create(title=title, description=description, is_private=is_private)
        admin_role = RoleModel.objects.get(id=1)
        project.roles.add(admin_role)
        RoleUserProjectModel.objects.create(role_id=1, project=project, user_id=user)

        project.users.add(user)

        project.save()

        return project


class SetProjectResolver(ProjectResolver):
    permission_classes = [IsAuthenticated, SetProjectPermission]

    @classmethod
    def resolver(cls, info, id: int, title: Optional[str] = None, description: Optional[str] = None,
                 is_private: Optional[bool] = None):
        info = get_info(info, id)
        cls.check_access(info)

        project = GetProjectResolver.resolver(info, id)

        if title:
            project.title = title

        if description:
            project.description = description

        if is_private is not None:
            project.is_private = is_private

        project.save()

        return project


class RemoveProjectResolver(ProjectResolver, RemoveResolver):
    permission_classes = [IsAuthenticated, RemoveProjectPermission]


class GetFolderResolver(FolderResolver, GetResolver):
    permission_classes = [IsAuthenticated, GetFolderPermission]


class AddFolderResolver(FolderResolver):
    permission_classes = [IsAuthenticated, AddFolderPermission]

    @classmethod
    @transaction.atomic()
    def resolver(cls, info, project_id: int, title: str, description: Optional[str] = None):
        info = get_info(info, project_id)
        cls.check_access(info)

        folder = cls.model.objects.create(title=title, description=description)
        cls.parent.model.objects.get(id=project_id).folders.add(folder)

        folder.save()

        return folder


class SetFolderResolver(FolderResolver):
    permission_classes = [IsAuthenticated, SetFolderPermission]

    @classmethod
    def resolver(cls, info, id: int, title: Optional[str] = None, description: Optional[str] = None):
        info = get_info(info, id)
        cls.check_access(info)

        folder = GetFolderResolver.resolver(info, id)

        if title:
            folder.title = title

        if description:
            folder.description = description

        folder.save()

        return folder


class RemoveFolderResolver(FolderResolver, RemoveResolver):
    permission_classes = [IsAuthenticated, RemoveFolderPermission]


class GetTaskResolver(TaskResolver, GetResolver):
    permission_classes = [IsAuthenticated, GetTaskPermission]


class AddTaskResolver(TaskResolver):
    permission_classes = [IsAuthenticated, AddTaskPermission]

    @classmethod
    @transaction.atomic()
    def resolver(cls, info, folder_id: int, title: str, description: Optional[str] = None,
                 date_time: Optional[datetime.datetime] = None):
        info = get_info(info, folder_id)
        cls.check_access(info)

        task = cls.model.objects.create(title=title, description=description, date_time=date_time)

        cls.parent.model.objects.get(id=folder_id).tasks.add(task)

        if date_time is not None:
            schedule_task(task)

            if not scheduler.running:
                scheduler.start()

        return task


class SetTaskResolver(TaskResolver):
    permission_classes = [IsAuthenticated, SetTaskPermission]

    @classmethod
    def resolver(cls, info, id: int, title: Optional[str] = None,
                 description: Optional[str] = None, is_finished: Optional[bool] = None,
                 date_time: Optional[datetime.datetime] = None):
        info = get_info(info, id)
        cls.check_access(info)

        task = GetTaskResolver.resolver(info, id)

        if title:
            task.title = title

        if description:
            task.description = description

        if is_finished is not None:
            task.is_finished = is_finished

        if date_time:
            task.date_time = date_time

        task.save()

        return task


class AddUserToTaskResolver(TaskResolver):
    permission_classes = [IsAuthenticated, SetTaskPermission]

    @classmethod
    def resolver(cls, info, id: int, user: int):
        info = get_info(info, id)
        cls.check_access(info)

        task = TasksModel.objects.get(id=id)

        task.users.add(user)

        return task


class RemoveTaskResolver(SubTaskResolver, RemoveResolver):
    permission_classes = [IsAuthenticated, RemoveTaskPermission]


class GetSubTaskResolver(SubTaskResolver, GetResolver):
    permission_classes = [IsAuthenticated, GetSubTaskPermission]


class AddSubTaskResolver(SubTaskResolver):
    permission_classes = [IsAuthenticated, AddSubTaskPermission]

    @classmethod
    @transaction.atomic()
    def resolver(cls, info, task_id: int, title: str,
                 description: Optional[str] = None):
        info = get_info(info, task_id)
        cls.check_access(info)

        subtask = cls.model.objects.create(title=title, description=description)

        cls.parent.model.objects.get(id=task_id).subtasks.add(subtask)

        return subtask


class SetSubTaskResolver(SubTaskResolver):
    permission_classes = [IsAuthenticated, SetSubTaskPermission]

    @classmethod
    def resolver(cls, info, id: int, title: Optional[str] = None,
                 description: Optional[str] = None, is_finished: Optional[bool] = None):
        info = get_info(info, id)
        cls.check_access(info)

        subtask = GetSubTaskResolver.resolver(info, id)

        if title:
            subtask.title = title

        if description:
            subtask.description = description

        if is_finished is not None:
            subtask.is_finished = is_finished

        subtask.save()

        return subtask


class RemoveSubTaskResolver(SubTaskResolver, RemoveResolver):
    permission_classes = [IsAuthenticated, RemoveSubTaskPermission]


class GetRoleResolver(GetResolver, RoleResolver):
    permission_classes = [IsAuthenticated, GetRolePermission]


class AddRoleResolver(RoleResolver):
    permission_classes = [IsAuthenticated, AddRolePermission]

    @classmethod
    @transaction.atomic()
    def resolver(cls, info, project_id: int, title: str, create: bool, update: bool,
                 delete: bool, role_management: bool, user_management: bool):
        info = get_info(info, project_id)
        cls.check_access(info)

        role = RoleModel.objects.create(title=title, create=create, update=update, delete=delete,
                                        role_management=role_management, user_management=user_management)

        ProjectsModel.objects.get(id=project_id).roles.add(role)

        return role


class SetRoleResolver(RoleResolver):
    permission_classes = [IsAuthenticated, SetRolePermission]

    @classmethod
    def resolver(cls, info, id: int, title: Optional[str] = None, create: Optional[bool] = None,
                 update: Optional[bool] = None, delete: Optional[bool] = None,
                 role_management: Optional[bool] = None, user_management: Optional[bool] = None):
        info = get_info(info, id)
        cls.check_access(info)

        role = RoleModel.objects.get(id=id)

        if title:
            role.title = title

        if create is not None:
            role.create = create

        if update is not None:
            role.update = update

        if delete is not None:
            role.delete = delete

        if role_management is not None:
            role.role_management = role_management

        if user_management is not None:
            role.user_management = user_management

        role.save()

        return role


class RemoveRoleResolver(RemoveResolver, RoleResolver):
    permission_classes = [IsAuthenticated, RemoveRolePermission]


class RoleAssignmentResolver(RoleUserProjectResolver):
    permission_classes = [IsAuthenticated, RoleAssignmentPermission]

    @classmethod
    def resolver(cls, info, user_id: int, project_id: int, role_id: int):
        info = get_info(info, project_id)
        cls.check_access(info)

        obj = cls.model.objects.get(user=user_id, project=project_id)
        role = RoleModel.objects.get(id=role_id)
        obj.role = role

        obj.save()

        return obj


class GetUserResolver(RoleUserProjectResolver):
    permission_classes = [IsAuthenticated, GetUserPermission]

    @classmethod
    def resolver(cls, info, user_id: int, project_id: int):
        info = get_info(info, project_id)
        cls.check_access(info)

        user = cls.model.objects.get(user_id=user_id, project_id=project_id)

        return user


class InviteUserResolver(RoleUserProjectResolver):
    permission_classes = [IsAuthenticated, UserManagementPermission]

    @classmethod
    def resolver(cls, info, user_id: int, project_id: int):
        info = get_info(info, project_id)
        cls.check_access(info)

        if len(RoleUserProjectResolver.model.objects.filter(user_id=user_id, project_id=project_id)) != 0:
            raise GraphQLError('The user is already a member of the project')

        user = info.context.request.user

        obj = cls.model.objects.get(user=user.id, project=project_id)

        try:
            role = obj.project.default_role

        except ObjectDoesNotExist:
            role = RoleModel.objects.get(id=2)

        project = ProjectsModel.objects.get(id=project_id)
        project.roles.add(role)

        invited_user = RoleUserProjectResolver.model.objects.create(user_id=user_id, project_id=project_id, role=role)

        invited_user.save()

        return invited_user


class RemoveUserResolver(RoleUserProjectResolver):
    permission_classes = [IsAuthenticated, UserManagementPermission]

    @classmethod
    def resolver(cls, info, user_id: int, project_id: int):
        info = get_info(info, project_id)
        cls.check_access(info)

        cls.model.objects.get(user_id=user_id, project_id=project_id).delete()

        return True


class GetTagResolver(TagResolver, GetResolver):
    permission_classes = [IsAuthenticated, GetTagPermission]


class AddTagResolver(TagResolver):
    permission_classes = [IsAuthenticated, AddTagPermission]

    @classmethod
    @transaction.atomic()
    def resolver(cls, info, project_id: int, title: str, color: Optional[str] = '#ffffff'):
        info = get_info(info, project_id)
        cls.check_access(info)

        tag = cls.model.objects.create(title=title, color=color)
        project = ProjectsModel.objects.get(id=project_id)
        project.tags.add(tag)

        project.save()

        return tag


class SetTagResolver(TagResolver):
    permission_classes = [IsAuthenticated, SetTagPermission]

    @classmethod
    @transaction.atomic()
    def resolver(cls, info, id: int, title: Optional[str], color: Optional[str] = None):
        info = get_info(info, id)
        cls.check_access(info)

        tag = cls.model.objects.get(id=id)

        if title:
            tag.title = title

        if color:
            tag.color = color

        return tag


class RemoveTagResolver(RemoveResolver, TagResolver):
    permission_classes = [IsAuthenticated, RemoveTagPermission]


class AddTagToTaskResolver(TagResolver):
    permission_classes = [IsAuthenticated, SetTagPermission]

    @classmethod
    def resolver(cls, info, task_id: int, tag_id: int):
        info = get_info(info, tag_id)
        cls.check_access(info)

        tag = cls.model.objects.get(id=tag_id)
        task = TasksModel.objects.get(id=task_id)

        task.tags.add(tag)

        task.save()

        return task


class RemoveTagFromTaskResolver(TagResolver):
    permission_classes = [IsAuthenticated, RemoveTagPermission]

    @classmethod
    def resolver(cls, info, task_id: int, tag_id: int):
        info = get_info(info, tag_id)
        cls.check_access(info)

        tag = cls.model.objects.get(id=tag_id)
        task = TasksModel.objects.get(id=task_id)

        task.tags.remove(tag)

        return True


class RegisterResolver(UserResolver):
    permission_classes = [IsNotAuthenticated]

    @classmethod
    def resolver(cls, info, username: str, password: str, email: str):
        cls.check_access(info)

        try:
            User.objects.get(username)
            raise GraphQLError('User with this username is already taken.')

        except ObjectDoesNotExist:
            pass

        user = User.objects.create_user(username=username, password=password, email=email)

        return user


class LoginResolver(UserResolver):
    permission_classes = [IsNotAuthenticated]

    @classmethod
    def resolver(cls, info, username: str, password: str):
        cls.check_access(info)

        user = User.objects.filter(username=username).first()

        if user is None or not user.check_password(password):
            raise GraphQLError("Invalid username or password")

        access_token = AccessToken().generate_token(user)
        refresh_token = RefreshToken().generate_token(user)

        return TokensType(access_token, refresh_token)


class RefreshTokenResolver:

    @classmethod
    def resolver(cls, info, refresh_token: str):
        if not check_refresh_token(refresh_token):
            raise GraphQLError('Invalid refresh_token')

        user_id = eval(decode(refresh_token).split(".")[1])['user_id']

        user = User.objects.get(id=user_id)

        access_token = AccessToken().generate_token(user)
        refresh_token = RefreshToken().generate_token(user)

        return TokensType(access_token, refresh_token)


class GetUserNotifications(NotificationResolver):
    permission_classes = [IsAuthenticated]

    @classmethod
    def resolver(cls, info):
        cls.check_access(info)

        user = info.context.request.user

        return list(cls.model.objects.filter(user=user.id))





