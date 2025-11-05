from django.contrib import admin
from django.contrib.auth.admin import UserAdmin


from .models import (Worker,
                     Task,
                     TaskType,
                     Position,
                     )


@admin.register(Worker)
class WorkerAdmin(UserAdmin):
    list_display = ("username", "email", "position")


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ("name", "deadline", "priority", "task_type")
    filter_horizontal = ("assignees",)


@admin.register(TaskType)
class TaskTypeAdmin(admin.ModelAdmin):
    list_display = ("name",)


@admin.register(Position)
class PositionAdmin(admin.ModelAdmin):
    list_display = ("name",)
