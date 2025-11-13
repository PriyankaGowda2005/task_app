"""
Task Model for Task Management Application

This model represents a task with the following fields:
- title: The task title (required, max 100 characters)
- description: Optional task description
- created_at: Automatically set when task is created
- updated_at: Automatically updated when task is modified
- completed: Boolean flag to mark task as complete/incomplete
"""

from django.db import models
from django.utils import timezone


class Task(models.Model):
    """
    Task model representing a single task item.
    
    Demonstrates Django ORM concepts:
    - CharField for short text
    - TextField for longer text
    - DateTimeField with auto_now_add and auto_now
    - BooleanField for true/false values
    """
    
    title = models.CharField(max_length=100, help_text="Task title (max 100 characters)")
    description = models.TextField(blank=True, null=True, help_text="Optional task description")
    created_at = models.DateTimeField(auto_now_add=True, help_text="Date and time when task was created")
    updated_at = models.DateTimeField(auto_now=True, help_text="Date and time when task was last updated")
    completed = models.BooleanField(default=False, help_text="Whether the task is completed")
    
    class Meta:
        """
        Meta class for model configuration.
        - ordering: Default ordering for queries (newest first)
        - verbose_name: Human-readable name for single object
        - verbose_name_plural: Human-readable name for multiple objects
        """
        ordering = ['-created_at']  # Newest tasks first
        verbose_name = 'Task'
        verbose_name_plural = 'Tasks'
    
    def __str__(self):
        """
        String representation of the Task object.
        Returns the task title for easy identification.
        """
        return self.title
    
    def get_status_display(self):
        """
        Returns a human-readable status string.
        Useful for displaying in templates.
        """
        return "Completed" if self.completed else "Pending"

