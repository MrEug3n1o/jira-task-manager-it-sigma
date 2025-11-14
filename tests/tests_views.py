from datetime import date, timedelta
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from task_manager.models import (
    Task, TaskType, Teams, Worker, Project, Position
)
from task_manager.forms import TaskCreateForm, TaskUpdateForm

User = get_user_model()


class SetupMixin(TestCase):

    def setUp(self):
        # Create positions
        self.position_dev = Position.objects.create(name="Developer")
        self.position_manager = Position.objects.create(name="Manager")

        # Create teams
        self.team_backend = Teams.objects.create(name="Backend Team")
        self.team_frontend = Teams.objects.create(name="Frontend Team")

        # Create projects
        self.project_website = Project.objects.create(name="Website Redesign")
        self.project_mobile = Project.objects.create(name="Mobile App")

        # Create task types
        self.task_type_bug = TaskType.objects.create(name="Bug Fix")
        self.task_type_feature = TaskType.objects.create(name="Feature")

        # Create workers
        self.worker1 = Worker.objects.create_user(
            username="testuser1",
            password="testpass123",
            position=self.position_dev,
            team=self.team_backend,
            first_name="John",
            last_name="Doe"
        )

        self.worker2 = Worker.objects.create_user(
            username="testuser2",
            password="testpass123",
            position=self.position_manager,
            team=self.team_frontend,
            first_name="Jane",
            last_name="Smith"
        )

        # Create tasks
        self.task_assigned = Task.objects.create(
            name="Test Assigned Task",
            description="Test Description for assigned task",
            deadline=date.today() + timedelta(days=7),
            priority=Task.Priority.HIGH,
            task_type=self.task_type_bug,
            project=self.project_website
        )
        self.task_assigned.assignees.add(self.worker1)

        self.task_unassigned = Task.objects.create(
            name="Test Unassigned Task",
            description="Test Description for unassigned task",
            deadline=date.today() + timedelta(days=14),
            priority=Task.Priority.MEDIUM,
            task_type=self.task_type_feature,
            project=self.project_mobile
        )

        # Login with worker1
        self.client.login(username="testuser1", password="testpass123")


class HomepageViewTests(SetupMixin):

    def test_homepage_view_status_code(self):
        url = reverse("task_manager:homepage")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_homepage_uses_correct_template(self):
        url = reverse("task_manager:homepage")
        response = self.client.get(url)
        self.assertTemplateUsed(response, "task_manager/homepage.html")

    def test_homepage_context_data(self):
        url = reverse("task_manager:homepage")
        response = self.client.get(url)
        self.assertIn("all_tasks_list", response.context)
        self.assertEqual(len(response.context["all_tasks_list"]), 2)

    def test_homepage_pagination(self):
        # Create more tasks to test pagination
        for i in range(15):
            Task.objects.create(
                name=f"Task {i}",
                description=f"Description {i}",
                deadline=date.today() + timedelta(days=i),
                priority=Task.Priority.LOW,
                task_type=self.task_type_bug,
                project=self.project_website
            )

        url = reverse("task_manager:homepage")
        response = self.client.get(url)
        self.assertEqual(len(response.context["all_tasks_list"]), 10)  # paginate_by = 10


class TaskListViewTests(SetupMixin):

    def test_task_list_view_status_code(self):
        url = reverse("task_manager:task-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_task_list_uses_correct_template(self):
        url = reverse("task_manager:task-list")
        response = self.client.get(url)
        self.assertTemplateUsed(response, "task_manager/task_list.html")

    def test_task_list_shows_only_assigned_tasks(self):
        url = reverse("task_manager:task-list")
        response = self.client.get(url)
        tasks = response.context["worker_tasks_list"]

        self.assertIn(self.task_assigned, tasks)
        self.assertNotIn(self.task_unassigned, tasks)

    def test_task_list_ordering(self):
        # Create another task with earlier deadline for the same worker
        early_task = Task.objects.create(
            name="Early Task",
            description="Early deadline task",
            deadline=date.today() + timedelta(days=1),
            priority=Task.Priority.LOW,
            task_type=self.task_type_bug,
            project=self.project_website
        )
        early_task.assignees.add(self.worker1)

        url = reverse("task_manager:task-list")
        response = self.client.get(url)
        tasks = list(response.context["worker_tasks_list"])

        # The task with earliest deadline should be first
        self.assertEqual(tasks[0], early_task)


class TaskDetailViewTests(SetupMixin):

    def test_task_detail_view_status_code(self):
        url = reverse("task_manager:task-detail", kwargs={"pk": self.task_assigned.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_task_detail_uses_correct_template(self):
        url = reverse("task_manager:task-detail", kwargs={"pk": self.task_assigned.pk})
        response = self.client.get(url)
        self.assertTemplateUsed(response, "task_manager/task_detail.html")

    def test_task_detail_view_404_for_invalid_task(self):
        url = reverse("task_manager:task-detail", kwargs={"pk": 9999})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)


class TaskCreateViewTests(SetupMixin):

    def test_task_create_view_status_code(self):
        url = reverse("task_manager:task-create")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_task_create_uses_correct_template(self):
        url = reverse("task_manager:task-create")
        response = self.client.get(url)
        self.assertTemplateUsed(response, "task_manager/task_form.html")

    def test_task_create_form_in_context(self):
        url = reverse("task_manager:task-create")
        response = self.client.get(url)
        self.assertIsInstance(response.context["form"], TaskCreateForm)

    def test_task_create_post_success(self):
        url = reverse("task_manager:task-create")
        data = {
            "name": "New Test Task",
            "description": "New task description",
            "deadline": date.today() + timedelta(days=10),
            "priority": Task.Priority.HIGH,
            "task_type": self.task_type_bug.pk,
            "assignees": [self.worker1.pk, self.worker2.pk],
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)  # Redirect after success
        self.assertRedirects(response, reverse("task_manager:task-list"))

        # Check if task was created
        self.assertTrue(Task.objects.filter(name="New Test Task").exists())

    def test_task_create_post_invalid_data(self):
        url = reverse("task_manager:task-create")
        data = {
            "name": "",  # Invalid: empty name
            "description": "Test description",
            "deadline": date.today() + timedelta(days=10),
            "priority": Task.Priority.HIGH,
            "task_type": self.task_type_bug.pk,
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)  # Stays on same page
        self.assertFormError(response, "form", "name", "This field is required.")


class TaskUpdateViewTests(SetupMixin):

    def test_task_update_view_status_code(self):
        url = reverse("task_manager:task-update", kwargs={"pk": self.task_assigned.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_task_update_uses_correct_template(self):
        url = reverse("task_manager:task-update", kwargs={"pk": self.task_assigned.pk})
        response = self.client.get(url)
        self.assertTemplateUsed(response, "task_manager/task_form.html")

    def test_task_update_form_in_context(self):
        url = reverse("task_manager:task-update", kwargs={"pk": self.task_assigned.pk})
        response = self.client.get(url)
        self.assertIsInstance(response.context["form"], TaskUpdateForm)

    def test_task_update_post_success(self):
        url = reverse("task_manager:task-update", kwargs={"pk": self.task_assigned.pk})
        data = {
            "name": "Updated Task Name",
            "description": "Updated description",
            "deadline": date.today() + timedelta(days=5),
            "is_completed": True,
            "priority": Task.Priority.CRITICAL,
            "task_type": self.task_type_feature.pk,
            "assignees": [self.worker1.pk],
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("task_manager:task-list"))

        # Check if task was updated
        updated_task = Task.objects.get(pk=self.task_assigned.pk)
        self.assertEqual(updated_task.name, "Updated Task Name")
        self.assertTrue(updated_task.is_completed)


class TaskDeleteViewTests(SetupMixin):

    def test_task_delete_view_status_code(self):
        url = reverse("task_manager:task-delete", kwargs={"pk": self.task_assigned.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_task_delete_uses_correct_template(self):
        url = reverse("task_manager:task-delete", kwargs={"pk": self.task_assigned.pk})
        response = self.client.get(url)
        self.assertTemplateUsed(response, "task_manager/task_confirm_delete.html")

    def test_task_delete_post_success(self):
        url = reverse("task_manager:task-delete", kwargs={"pk": self.task_assigned.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("task_manager:task-list"))

        # Check if task was deleted
        self.assertFalse(Task.objects.filter(pk=self.task_assigned.pk).exists())


class WorkerListViewTests(SetupMixin):

    def test_worker_list_view_status_code(self):
        url = reverse("task_manager:worker-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_worker_list_uses_correct_template(self):
        url = reverse("task_manager:worker-list")
        response = self.client.get(url)
        self.assertTemplateUsed(response, "task_manager/worker_list.html")

    def test_worker_list_context_data(self):
        url = reverse("task_manager:worker-list")
        response = self.client.get(url)
        self.assertIn("workers", response.context)
        self.assertEqual(len(response.context["workers"]), 2)

    def test_worker_list_search_functionality(self):
        # Search by username
        url = reverse("task_manager:worker-list") + "?q=testuser1"
        response = self.client.get(url)
        self.assertEqual(len(response.context["workers"]), 1)
        self.assertEqual(response.context["workers"][0], self.worker1)

        # Search by first name
        url = reverse("task_manager:worker-list") + "?q=John"
        response = self.client.get(url)
        self.assertEqual(len(response.context["workers"]), 1)
        self.assertEqual(response.context["workers"][0], self.worker1)

        # Search by team name
        url = reverse("task_manager:worker-list") + "?q=Backend"
        response = self.client.get(url)
        self.assertEqual(len(response.context["workers"]), 1)
        self.assertEqual(response.context["workers"][0], self.worker1)

        # Search with no results
        url = reverse("task_manager:worker-list") + "?q=Nonexistent"
        response = self.client.get(url)
        self.assertEqual(len(response.context["workers"]), 0)


class WorkerDetailViewTests(SetupMixin):

    def test_worker_detail_view_status_code(self):
        url = reverse("task_manager:worker-detail", kwargs={"pk": self.worker1.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_worker_detail_uses_correct_template(self):
        url = reverse("task_manager:worker-detail", kwargs={"pk": self.worker1.pk})
        response = self.client.get(url)
        self.assertTemplateUsed(response, "task_manager/worker_detail.html")

    def test_worker_detail_context_data(self):
        url = reverse("task_manager:worker-detail", kwargs={"pk": self.worker1.pk})
        response = self.client.get(url)
        self.assertIn("tasks", response.context)
        self.assertEqual(len(response.context["tasks"]), 1)
        self.assertEqual(response.context["tasks"][0], self.task_assigned)


class TeamListViewTests(SetupMixin):

    def test_team_list_view_status_code(self):
        url = reverse("task_manager:team-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_team_list_uses_correct_template(self):
        url = reverse("task_manager:team-list")
        response = self.client.get(url)
        self.assertTemplateUsed(response, "task_manager/team_list.html")

    def test_team_list_context_data(self):
        url = reverse("task_manager:team-list")
        response = self.client.get(url)
        self.assertIn("teams", response.context)
        self.assertEqual(len(response.context["teams"]), 2)

    def test_team_list_pagination(self):
        # Create more teams to test pagination
        for i in range(5):
            Teams.objects.create(name=f"Team {i}")

        url = reverse("task_manager:team-list")
        response = self.client.get(url)
        self.assertEqual(len(response.context["teams"]), 3)  # paginate_by = 3


class TeamDetailViewTests(SetupMixin):

    def test_team_detail_view_status_code(self):
        url = reverse("task_manager:team-detail", kwargs={"pk": self.team_backend.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_team_detail_uses_correct_template(self):
        url = reverse("task_manager:team-detail", kwargs={"pk": self.team_backend.pk})
        response = self.client.get(url)
        self.assertTemplateUsed(response, "task_manager/team_detail.html")

    def test_team_detail_context_data(self):
        url = reverse("task_manager:team-detail", kwargs={"pk": self.team_backend.pk})
        response = self.client.get(url)
        self.assertIn("members", response.context)
        self.assertEqual(len(response.context["members"]), 1)
        self.assertEqual(response.context["members"][0], self.worker1)


class ProjectListViewTests(SetupMixin):

    def test_project_list_view_status_code(self):
        url = reverse("task_manager:project-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_project_list_uses_correct_template(self):
        url = reverse("task_manager:project-list")
        response = self.client.get(url)
        self.assertTemplateUsed(response, "task_manager/project_list.html")

    def test_project_list_context_data(self):
        url = reverse("task_manager:project-list")
        response = self.client.get(url)
        self.assertIn("projects", response.context)
        self.assertEqual(len(response.context["projects"]), 2)

    def test_project_list_pagination(self):
        # Create more projects to test pagination
        for i in range(5):
            Project.objects.create(name=f"Project {i}")

        url = reverse("task_manager:project-list")
        response = self.client.get(url)
        self.assertEqual(len(response.context["projects"]), 3)  # paginate_by = 3


class ProjectDetailViewTests(SetupMixin):

    def test_project_detail_view_status_code(self):
        url = reverse("task_manager:project-detail", kwargs={"pk": self.project_website.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_project_detail_uses_correct_template(self):
        url = reverse("task_manager:project-detail", kwargs={"pk": self.project_website.pk})
        response = self.client.get(url)
        self.assertTemplateUsed(response, "task_manager/project_detail.html")

    def test_project_detail_context_data(self):
        url = reverse("task_manager:project-detail", kwargs={"pk": self.project_website.pk})
        response = self.client.get(url)
        self.assertIn("tasks", response.context)
        self.assertEqual(len(response.context["tasks"]), 1)
        self.assertEqual(response.context["tasks"][0], self.task_assigned)


class LoginRequiredTests(SetupMixin):

    def test_all_views_require_login(self):
        views_to_test = [
            reverse("task_manager:homepage"),
            reverse("task_manager:task-list"),
            reverse("task_manager:task-detail", kwargs={"pk": self.task_assigned.pk}),
            reverse("task_manager:task-create"),
            reverse("task_manager:task-update", kwargs={"pk": self.task_assigned.pk}),
            reverse("task_manager:task-delete", kwargs={"pk": self.task_assigned.pk}),
            reverse("task_manager:worker-list"),
            reverse("task_manager:worker-detail", kwargs={"pk": self.worker1.pk}),
            reverse("task_manager:team-list"),
            reverse("task_manager:team-detail", kwargs={"pk": self.team_backend.pk}),
            reverse("task_manager:project-list"),
            reverse("task_manager:project-detail", kwargs={"pk": self.project_website.pk}),
        ]

        self.client.logout()

        for url in views_to_test:
            response = self.client.get(url)
            self.assertNotEqual(response.status_code, 200)
            # Should redirect to login page
            self.assertEqual(response.status_code, 302)
            self.assertTrue(response.url.startswith('/accounts/login/'))
