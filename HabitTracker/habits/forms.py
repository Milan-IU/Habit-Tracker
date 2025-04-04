from django import forms
from .models import Habit, HabitCompletion

class HabitForm(forms.ModelForm):
    """
    Form for creating and editing habits.
    
    This form allows users to create new habits or edit existing ones.
    It provides fields for the habit's title, description, and frequency.
    The user field is automatically set based on the current user.

    Attributes:
        title: CharField for the habit name
        description: TextField for detailed habit description
        frequency: CharField with choices for habit frequency
    """

    class Meta:
        model = Habit
        fields = ['title', 'description', 'frequency']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }

class HabitCompletionForm(forms.ModelForm):
    """
    Form for recording habit completions.
    
    This form allows users to mark a habit as completed and add optional notes
    about the completion. The habit field is automatically set based on the
    context, and the completed_at field defaults to the current time.

    Attributes:
        notes: TextField for optional notes about the completion
    """

    class Meta:
        model = HabitCompletion
        fields = ['notes']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3}),
        } 