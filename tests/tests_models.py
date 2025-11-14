from django.test import TestCase
from django.contrib.auth import get_user_model
from datetime import date, timedelta

from task_manager.models import Position, Teams, Project, Worker, TaskType, Task

User = get_user_model()


class MinimalModelTests(TestCase):

    def test_basic_model_creation(self):
        position = Position.objects.create(name="Developer")
        team = Teams.objects.create(name="Backend Team")
        project = Project.objects.create(name="Website Redesign")
        task_type = TaskType.objects.create(name="Bug Fix")

        worker = Worker.objects.create_user(
            username="testuser",
            password="testpass123",
            position=position,
            team=team
        )

        task = Task.objects.create(
            name="Test Task",
            description="Test Description",
            deadline=date.today() + timedelta(days=7),
            priority=Task.Priority.HIGH,
            task_type=task_type,
            project=project
        )
        task.assignees.add(worker)

        self.assertEqual(Position.objects.count(), 1)
        self.assertEqual(Teams.objects.count(), 1)
        self.assertEqual(Project.objects.count(), 1)
        self.assertEqual(TaskType.objects.count(), 1)
        self.assertEqual(Worker.objects.count(), 1)
        self.assertEqual(Task.objects.count(), 1)

        self.assertEqual(worker.tasks.count(), 1)
        self.assertEqual(project.tasks.count(), 1)
        self.assertEqual(team.members.count(), 1)
        self.assertEqual(position.workers.count(), 1)
