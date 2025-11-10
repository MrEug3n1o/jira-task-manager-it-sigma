from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import (
Worker, Task, Team, Project
)
from .forms import TaskCreateForm, TaskUpdateForm, TaskDeleteForm


class Homepage(LoginRequiredMixin, generic.ListView):
    model = Task
    context_object_name = "all_tasks_list"
    template_name = "task_manager/homepage.html"
    paginate_by = 10


class TaskListView(LoginRequiredMixin, generic.ListView):
    model = Task
    context_object_name = "worker_tasks_list"
    template_name = "task_manager/task_list.html"
    paginate_by = 10

    def get_queryset(self):
        return Task.objects.filter(assignees=self.request.user).order_by("deadline")


class TaskDetailView(LoginRequiredMixin, generic.DetailView):
    model = Task
    template_name = "task_manager/task_detail.html"


class TaskCreateView(LoginRequiredMixin, generic.CreateView):
    model = Task
    form_class = TaskCreateForm
    template_name = "task_manager/task_form.html"
    success_url = reverse_lazy("task_manager:task-list")


class TaskUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Task
    form_class = TaskUpdateForm
    template_name = "task_manager/task_form.html"
    success_url = reverse_lazy("task_manager:task-list")


class TaskDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Task
    form_class = TaskDeleteForm
    template_name = "task_manager/task_confirm_delete.html"
    success_url = reverse_lazy("task_manager:task-list")

class WorkerListView(LoginRequiredMixin, generic.ListView):
    model = Worker
    template_name = "task_manager/worker_list.html"
    context_object_name = "workers"


class WorkerDetailView(LoginRequiredMixin, generic.DetailView):
    model = Worker
    template_name = "task_manager/worker_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["tasks"] = self.object.tasks.all()
        return context


class TeamListView(LoginRequiredMixin, generic.ListView):
    model = Team
    template_name = "task_manager/teams_list.html"
    context_object_name = "teams"
    paginate_by = 3


class TeamDetailView(LoginRequiredMixin, generic.DetailView):
    model = Team
    template_name = "task_manager/teams_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["members"] = self.object.members.all()
        return context


class ProjectListView(LoginRequiredMixin, generic.ListView):
    model = Project
    template_name = "task_manager/project_list.html"
    context_object_name = "projects"
    paginate_by = 3


class ProjectDetailView(LoginRequiredMixin, generic.DetailView):
    model = Project
    template_name = "task_manager/project_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["tasks"] = self.object.tasks.all()
        return context