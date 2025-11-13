"""
Django Admin Configuration for Task Model

This file registers the Task model with Django's admin interface,
allowing administrators to manage tasks through the admin panel.
"""

from django.contrib import admin
from .models import Task


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    """
    Admin configuration for Task model.
    
    This class customizes how tasks appear in the Django admin interface.
    """
    
    # Fields to display in the list view
    list_display = ['title', 'completed', 'created_at', 'updated_at']
    
    # Fields that can be used for filtering
    list_filter = ['completed', 'created_at', 'updated_at']
    
    # Fields that can be searched
    search_fields = ['title', 'description']
    
    # Fields that are read-only (auto-generated)
    readonly_fields = ['created_at', 'updated_at']
    
    # Fields to display in the detail/edit form
    fieldsets = (
        ('Task Information', {
            'fields': ('title', 'description')
        }),
        ('Status', {
            'fields': ('completed',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)  # Collapsible section
        }),
    )
    
    # Ordering in admin list view
    ordering = ['-created_at']    