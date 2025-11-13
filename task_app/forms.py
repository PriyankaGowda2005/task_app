"""
Django Forms for Task Management

This file contains form classes for creating and editing tasks.
Forms provide validation and HTML generation for user input.
"""

from django import forms
from .models import Task


class TaskForm(forms.ModelForm):
    """
    Form for creating and editing tasks.
    
    Uses ModelForm which automatically generates form fields
    based on the Task model. This demonstrates Django's DRY principle.
    """
    
    class Meta:
        model = Task
        fields = ['title', 'description', 'completed']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter task title...',
                'required': True
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Enter task description (optional)...'
            }),
            'completed': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
        labels = {
            'title': 'Task Title',
            'description': 'Description',
            'completed': 'Mark as Completed'
        }
        help_texts = {
            'title': 'Enter a descriptive title for your task (max 100 characters)',
            'description': 'Add any additional details about the task (optional)',
        }
    
    def __init__(self, *args, **kwargs):
        """
        Customize form initialization.
        We can add custom styling or behavior here.
        """
        super().__init__(*args, **kwargs)
        # Make title field required
        self.fields['title'].required = True

