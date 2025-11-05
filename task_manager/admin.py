from django.contrib import admin
from django.contrib.auth.admin import UserAdmin


from .models import (Worker,
                     Task,
                     TaskType,
                     Position,
                    Team,
                    Project,
                     )


@admin.register(Worker)
class WorkerAdmin(UserAdmin):
    list_display = ("username", "email", "position", "team")


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ("name", "deadline", "priority", "task_type", "project")
    filter_horizontal = ("assignees",)


@admin.register(TaskType)
class TaskTypeAdmin(admin.ModelAdmin):
    list_display = ("name",)


@admin.register(Position)
class PositionAdmin(admin.ModelAdmin):
    list_display = ("name",)


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("name", "get_tasks")
    readonly_fields = ("get_tasks",)


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ("name", "get_workers")
    readonly_fields = ("get_workers",)
