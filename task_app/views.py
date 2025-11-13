"""
Django Views for Task Management Application

This file contains function-based views that handle HTTP requests
and return HTTP responses. Demonstrates Django's MVT architecture:
- Model: Task (defined in models.py)
- View: These functions (views.py)
- Template: HTML templates in templates/tasks/
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Task
from .forms import TaskForm


def task_list(request):
    """
    View function to display a list of all tasks.
    
    Handles:
    - Displaying all tasks or filtered tasks
    - Search functionality
    - Pagination
    - Filtering by completion status
    
    URL: / (root URL)
    """
    # Get all tasks from database
    tasks = Task.objects.all()
    
    # Handle search query
    search_query = request.GET.get('search', '')
    if search_query:
        # Filter tasks by title or description containing search query
        tasks = tasks.filter(
            Q(title__icontains=search_query) | 
            Q(description__icontains=search_query)
        )
        messages.info(request, f'Found {tasks.count()} task(s) matching "{search_query}"')
    
    # Handle filter by completion status
    filter_status = request.GET.get('filter', '')
    if filter_status == 'completed':
        tasks = tasks.filter(completed=True)
    elif filter_status == 'pending':
        tasks = tasks.filter(completed=False)
    
    # Pagination: Show 6 tasks per page
    paginator = Paginator(tasks, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Context dictionary: data passed to template
    context = {
        'tasks': page_obj,
        'search_query': search_query,
        'filter_status': filter_status,
        'total_tasks': Task.objects.count(),
        'completed_tasks': Task.objects.filter(completed=True).count(),
        'pending_tasks': Task.objects.filter(completed=False).count(),
    }
    
    # Render the template with context data
    return render(request, 'tasks/task_list.html', context)


def add_task(request):
    """
    View function to add a new task.
    
    Handles:
    - GET request: Display empty form
    - POST request: Process form data and save task
    
    URL: /add/
    """
    if request.method == 'POST':
        # Create form instance with POST data
        form = TaskForm(request.POST)
        
        if form.is_valid():
            # Save the task to database
            task = form.save()
            # Show success message
            messages.success(request, f'Task "{task.title}" added successfully!')
            # Redirect to task list
            return redirect('task_app:task_list')
        else:
            # Form has errors, show error message
            messages.error(request, 'Please correct the errors below.')
    else:
        # GET request: show empty form
        form = TaskForm()
    
    # Render form template
    context = {'form': form, 'action': 'Add'}
    return render(request, 'tasks/task_form.html', context)


def edit_task(request, id):
    """
    View function to edit an existing task.
    
    Handles:
    - GET request: Display form with existing task data
    - POST request: Process form data and update task
    
    URL: /edit/<id>/
    
    Args:
        id: Primary key of the task to edit
    """
    # Get task from database, return 404 if not found
    task = get_object_or_404(Task, id=id)
    
    if request.method == 'POST':
        # Create form instance with POST data and existing task instance
        form = TaskForm(request.POST, instance=task)
        
        if form.is_valid():
            # Save updated task
            task = form.save()
            # Show success message
            messages.success(request, f'Task "{task.title}" updated successfully!')
            # Redirect to task list
            return redirect('task_app:task_list')
        else:
            # Form has errors
            messages.error(request, 'Please correct the errors below.')
    else:
        # GET request: show form with existing task data
        form = TaskForm(instance=task)
    
    # Render form template
    context = {'form': form, 'task': task, 'action': 'Edit'}
    return render(request, 'tasks/task_form.html', context)


def delete_task(request, id):
    """
    View function to delete a task.
    
    Handles:
    - GET request: Show confirmation page
    - POST request: Delete the task
    
    URL: /delete/<id>/
    
    Args:
        id: Primary key of the task to delete
    """
    # Get task from database
    task = get_object_or_404(Task, id=id)
    
    if request.method == 'POST':
        # Store task title for success message
        task_title = task.title
        # Delete task from database
        task.delete()
        # Show success message
        messages.success(request, f'Task "{task_title}" deleted successfully!')
        # Redirect to task list
        return redirect('task_app:task_list')
    
    # GET request: show confirmation page
    context = {'task': task}
    return render(request, 'tasks/confirm_delete.html', context)


def toggle_task(request, id):
    """
    View function to toggle task completion status.
    
    Toggles the completed field between True and False.
    This is a simple action that doesn't require a form.
    
    URL: /toggle/<id>/
    
    Args:
        id: Primary key of the task to toggle
    """
    # Get task from database
    task = get_object_or_404(Task, id=id)
    
    # Toggle completion status
    task.completed = not task.completed
    task.save()  # Save changes to database
    
    # Show appropriate message
    status = "completed" if task.completed else "marked as pending"
    messages.success(request, f'Task "{task.title}" {status}!')
    
    # Redirect back to task list
    return redirect('task_app:task_list')

