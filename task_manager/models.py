from django.db import models
from django.contrib.auth.models import AbstractUser


class Position(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Team(models.Model):
    name = models.CharField(max_length=100, unique=True)
    #leader

    def get_workers(self):
        return ", ".join(worker.name for worker in self.members.all())

    get_workers.short_description = "Members"


class Project(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

    def get_tasks(self):
        return ", ".join(task.name for task in self.tasks.all())

    get_tasks.short_description = "Tasks"


class Worker(AbstractUser):
    position = models.ForeignKey(Position, on_delete=models.SET_NULL, null=True, related_name="workers")
    team = models.ForeignKey(Team, on_delete=models.SET_NULL, null=True, related_name="members")
    def __str__(self):
        return f"{self.username} ({self.position})" if self.position else self.username



class TaskType(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Task(models.Model):
    class Priority(models.TextChoices):
        LOW = "Low"
        MEDIUM = "Medium"
        HIGH = "High"
        CRITICAL = "Critical"

    name = models.CharField(max_length=200)
    description = models.TextField()
    deadline = models.DateField()
    is_completed = models.BooleanField(default=False)
    priority = models.CharField(
        max_length=10,
        choices=Priority.choices,
        default=Priority.MEDIUM
    )
    task_type = models.ForeignKey(TaskType, on_delete=models.CASCADE, related_name="tasks")
    assignees = models.ManyToManyField(Worker, related_name="tasks")
    project = models.ForeignKey(Project, on_delete=models.SET_NULL, null=True, related_name="tasks")
    def __str__(self):
        return f"{self.name} ({self.priority})"

    class Meta:
        ordering = ["deadline", "priority"]
