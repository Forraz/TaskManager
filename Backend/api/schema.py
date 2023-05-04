import datetime
from typing import List

import strawberry
from .resolvers import *
from .models import ProjectsModel, FoldersModel, TasksModel, SubTasksModel
from django.contrib.auth.models import User


@strawberry.django.type(TagsModel)
class TagType:
    id: int
    title: str
    color: str


@strawberry.django.type(User)
class UserType:
    id: int
    username: str


@strawberry.django.type(SubTasksModel)
class SubTaskType:
    id: int
    title: str
    description: str
    is_finished: bool


@strawberry.django.type(TasksModel)
class TaskType:
    id: int
    title: str
    description: str
    is_finished: bool
    date: datetime.date
    users: List[UserType]
    subtasks: List[SubTaskType]
    tags: List[TagType]


@strawberry.django.type(FoldersModel)
class FolderType:
    id: int
    title: str
    description: str
    tasks: List[TaskType]


@strawberry.django.type(RoleModel)
class RoleType:
    id: int
    title: str
    create: bool
    update: bool
    delete: bool
    role_management: bool
    user_management: bool


@strawberry.django.type(RoleUserProjectModel)
class RoleUserProjectType:
    id: int
    user: UserType
    role: RoleType


@strawberry.django.type(ProjectsModel)
class ProjectType:
    id: int
    title: str
    description: str
    is_private: bool
    folders: List[FolderType]
    users: List[UserType]
    roles: List[RoleType]
    tags: List[TagType]
    default_role: RoleType


@strawberry.type
class Query:
    get_project: ProjectType = strawberry.field(resolver=GetProjectResolver.resolver)
    get_user_projects: List[ProjectType] = strawberry.field(resolver=GetUserProjectsResolver.resolver)
    get_folder: FolderType = strawberry.field(resolver=GetFolderResolver.resolver)
    get_task: TaskType = strawberry.field(resolver=GetTaskResolver.resolver)
    get_subtask: SubTaskType = strawberry.field(resolver=GetSubTaskResolver.resolver)
    get_user: RoleUserProjectType = strawberry.field(resolver=GetUserResolver.resolver)
    get_tag: TagType = strawberry.field(resolver=GetTagResolver.resolver)
    get_role: RoleType = strawberry.field(resolver=GetRoleResolver.resolver)


@strawberry.type
class Mutation:
    register: UserType = strawberry.mutation(resolver=RegisterResolver.resolver)
    login: TokensType = strawberry.mutation(resolver=LoginResolver.resolver)
    refresh_token: TokensType = strawberry.mutation(resolver=RefreshTokenResolver.resolver)
    add_project: ProjectType = strawberry.mutation(resolver=AddProjectResolver.resolver)
    set_project: ProjectType = strawberry.mutation(resolver=SetProjectResolver.resolver)
    remove_project: bool = strawberry.mutation(resolver=RemoveProjectResolver.resolver)
    add_folder: FolderType = strawberry.mutation(resolver=AddFolderResolver.resolver)
    set_folder: FolderType = strawberry.mutation(resolver=SetFolderResolver.resolver)
    remove_folder: bool = strawberry.mutation(resolver=RemoveFolderResolver.resolver)
    add_task: TaskType = strawberry.mutation(resolver=AddTaskResolver.resolver)
    set_task: TaskType = strawberry.mutation(resolver=SetTaskResolver.resolver)
    remove_task: bool = strawberry.mutation(resolver=RemoveTaskResolver.resolver)
    add_subtask: SubTaskType = strawberry.mutation(resolver=AddSubTaskResolver.resolver)
    set_subtask: SubTaskType = strawberry.mutation(resolver=SetSubTaskResolver.resolver)
    remove_subtask: bool = strawberry.mutation(resolver=RemoveSubTaskResolver.resolver)
    add_role: RoleType = strawberry.mutation(resolver=AddRoleResolver.resolver)
    set_role: RoleType = strawberry.mutation(resolver=SetRoleResolver.resolver)
    remove_role: bool = strawberry.mutation(resolver=RemoveRoleResolver.resolver)
    assign_role: RoleUserProjectType = strawberry.mutation(resolver=RoleAssignmentResolver.resolver)
    invite_user: RoleUserProjectType = strawberry.mutation(resolver=InviteUserResolver.resolver)
    remove_user: bool = strawberry.mutation(resolver=RemoveUserResolver.resolver)
    add_tag: TagType = strawberry.mutation(resolver=AddTagResolver.resolver)
    set_tag: TagType = strawberry.mutation(resolver=SetTagResolver.resolver)
    remove_tag: bool = strawberry.mutation(resolver=RemoveTagResolver.resolver)
    add_tag_to_task: TaskType = strawberry.mutation(resolver=AddTagToTaskResolver.resolver)
    remove_tag_from_task: bool = strawberry.mutation(resolver=RemoveTagFromTaskResolver.resolver)


schema = strawberry.Schema(query=Query, mutation=Mutation)
