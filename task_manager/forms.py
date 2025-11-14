from django import forms
from .models import Task


class TaskCreateForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = [
            "name",
            "description",
            "deadline",
            "priority",
            "task_type",
            "assignees",
        ]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 3, "placeholder": "Enter task details..."}),
            "deadline": forms.DateInput(attrs={"type": "date"}),
            "assignees": forms.SelectMultiple(attrs={"size": 5}),
        }


class TaskUpdateForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = [
            "name",
            "description",
            "deadline",
            "is_completed",
            "priority",
            "task_type",
            "assignees",
        ]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 3}),
            "deadline": forms.DateInput(attrs={"type": "date"}),
        }


class TaskDeleteForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = []
