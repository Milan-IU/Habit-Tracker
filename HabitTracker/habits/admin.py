from django.contrib import admin
from .models import Habit, HabitCompletion

@admin.register(Habit)
class HabitAdmin(admin.ModelAdmin):
    """
    Admin configuration for the Habit model.
    
    This class customizes the display and filtering of habits in the Django admin interface.
    It allows for easy searching and filtering of habits by title, description, and creation date.
    """
    
    
    list_display = ('title', 'user', 'frequency', 'created_at')
    list_filter = ('frequency', 'created_at')
    search_fields = ('title', 'description')
    date_hierarchy = 'created_at'

@admin.register(HabitCompletion)
class HabitCompletionAdmin(admin.ModelAdmin):
    """
    Admin configuration for the HabitCompletion model.
    
    This class customizes the display and filtering of habit completions in the Django admin interface.
    It allows for easy searching and filtering of completions by habit and completion date.

    I must confess that I was to lazy to check the habits of for four weeks consistently. So i implemented this class to check them off manually for the given period.
    """
    list_display = ('habit', 'completed_at')
    list_filter = ('completed_at', 'habit')
    search_fields = ('habit__title', 'notes')
    date_hierarchy = 'completed_at'
