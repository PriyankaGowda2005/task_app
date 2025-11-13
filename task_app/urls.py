"""
URL Configuration for Tasks App

This file maps URL patterns to view functions.
Demonstrates Django URL routing and named URLs for reverse URL lookup.
"""

from django.urls import path
from . import views

# App name for namespacing URLs
app_name = 'task_app'

# URL patterns for the tasks app
urlpatterns = [
    # Task List - Root URL of tasks app
    path('', views.task_list, name='task_list'),
    
    # Add Task
    path('add/', views.add_task, name='add_task'),
    
    # Edit Task - <int:id> captures the task ID as an integer
    path('edit/<int:id>/', views.edit_task, name='edit_task'),
    
    # Delete Task
    path('delete/<int:id>/', views.delete_task, name='delete_task'),
    
    # Toggle Task Completion
    path('toggle/<int:id>/', views.toggle_task, name='toggle_task'),
]

