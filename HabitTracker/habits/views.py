from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Habit, HabitCompletion
from .forms import HabitForm, HabitCompletionForm
from django.utils import timezone
from datetime import timedelta
from django.db.models import Count, Max, Min
import json

@login_required
def habit_list(request):
    """
    Display a list of all habits for the current user.
    
    This view shows all habits that the logged-in user has created,
    ordered by creation date (newest first).

    Args:
        request: The HTTP request object.

    Returns:
        HttpResponse: Rendered template with the list of habits.
    """
    habits = Habit.objects.filter(user=request.user)
    return render(request, 'habits/habit_list.html', {'habits': habits})

@login_required
def habit_create(request):
    """
    Create a new habit.
    
    This view handles both GET and POST requests for creating a new habit.
    On GET, it displays the habit creation form.
    On POST, it processes the form data and creates a new habit if valid.

    Args:
        request: The HTTP request object.

    Returns:
        HttpResponse: Either the habit creation form or a redirect to the habit list
                     after successful creation.
    """
    if request.method == 'POST':
        form = HabitForm(request.POST)
        if form.is_valid():
            habit = form.save(commit=False)
            habit.user = request.user
            habit.save()
            messages.success(request, 'Habit created successfully!')
            return redirect('habits:habit_list')
    else:
        form = HabitForm()
    return render(request, 'habits/habit_form.html', {'form': form, 'title': 'Create New Habit'})

@login_required
def habit_detail(request, pk):
    """
    Display detailed information about a specific habit.
    
    This view shows the habit's details and its completion history.
    Only allows access to habits owned by the current user.

    Args:
        request: The HTTP request object.
        pk (int): The primary key of the habit to display.

    Returns:
        HttpResponse: Rendered template with the habit details and completion history.
    """
    habit = get_object_or_404(Habit, pk=pk, user=request.user)
    completions = habit.completions.all()
    return render(request, 'habits/habit_detail.html', {
        'habit': habit,
        'completions': completions
    })

@login_required
def habit_complete(request, pk):
    """
    Mark a habit as completed.
    
    This view handles both GET and POST requests for marking a habit as complete.
    On GET, it displays the completion form.
    On POST, it processes the form data and records the habit completion.

    Args:
        request: The HTTP request object.
        pk (int): The primary key of the habit to mark as complete.

    Returns:
        HttpResponse: Either the completion form or a redirect to the habit detail
                     page after successful completion.
    """
    habit = get_object_or_404(Habit, pk=pk, user=request.user)
    if request.method == 'POST':
        form = HabitCompletionForm(request.POST)
        if form.is_valid():
            completion = form.save(commit=False)
            completion.habit = habit
            completion.save()
            messages.success(request, 'Habit marked as completed!')
            return redirect('habits:habit_detail', pk=pk)
    else:
        form = HabitCompletionForm()
    return render(request, 'habits/habit_complete.html', {
        'form': form,
        'habit': habit
    })

@login_required
def habit_delete(request, pk):
    """
    Delete a specific habit.
    
    This view handles both GET and POST requests for deleting a habit.
    On GET, it displays the deletion confirmation form.
    On POST, it processes the deletion request and removes the habit.

    Args:
        request: The HTTP request object.
        pk (int): The primary key of the habit to delete.

    Returns:
        HttpResponse: Either the deletion confirmation form or a redirect to the habit list
                     after successful deletion.
    """
    habit = get_object_or_404(Habit, pk=pk, user=request.user)
    if request.method == 'POST':
        habit.delete()
        messages.success(request, 'Habit deleted successfully!')
        return redirect('habits:habit_list')
    return render(request, 'habits/habit_confirm_delete.html', {'habit': habit})

@login_required
def habit_edit(request, pk):
    """
    Edit an existing habit.
    
    This view handles both GET and POST requests for editing a habit.
    On GET, it displays the habit edit form pre-filled with the habit's data.
    On POST, it processes the form data and updates the habit if valid.
    Only allows editing of habits owned by the current user.

    Args:
        request: The HTTP request object.
        pk (int): The primary key of the habit to edit.

    Returns:
        HttpResponse: Either the habit edit form or a redirect to the habit list
                     after successful update.
    """
    habit = get_object_or_404(Habit, pk=pk, user=request.user)
    if request.method == 'POST':
        form = HabitForm(request.POST, instance=habit)
        if form.is_valid():
            form.save()
            messages.success(request, 'Habit updated successfully!')
            return redirect('habits:habit_list')
    else:
        form = HabitForm(instance=habit)
    return render(request, 'habits/habit_form.html', {
        'form': form,
        'title': 'Edit Habit',
        'habit': habit
    })

@login_required
def analysis_dashboard(request):
    """
    Display an analysis dashboard for the user's habits.
    
    This view provides various statistics about the user's habits, including:
    - Currently tracked habits
    - Habits grouped by periodicity (daily, weekly, monthly)
    - Longest overall tracking period
    - Individual habit tracking periods and streaks
    - Success rate chart for the last 7 days

    Args:
        request: The HTTP request object.

    Returns:
        HttpResponse: Rendered template with the analysis dashboard.
    """
    # Get currently tracked habits
    current_habits = Habit.objects.filter(user=request.user)
    
    # Calculate success rates for the last 7 days
    success_rates = []
    dates = []
    today = timezone.now().date()
    
    for i in range(6, -1, -1):  # Last 7 days
        date = today - timedelta(days=i)
        dates.append(date.strftime('%Y-%m-%d'))
        
        total_habits = current_habits.count()
        if total_habits == 0:
            success_rates.append(0)
            continue

        successful_habits = 0
        for habit in current_habits:
            # Check if habit was completed on this date based on its frequency
            if habit.frequency == 'daily':
                if habit.completions.filter(completed_at__date=date).exists():
                    successful_habits += 1
            elif habit.frequency == 'weekly':
                # Check if completed in the week containing this date
                week_start = date - timedelta(days=date.weekday())
                week_end = week_start + timedelta(days=6)
                if habit.completions.filter(completed_at__date__range=[week_start, week_end]).exists():
                    successful_habits += 1
            elif habit.frequency == 'monthly':
                # Check if completed in the month containing this date
                month_start = date.replace(day=1)
                if date.month == 12:
                    next_month = date.replace(year=date.year + 1, month=1, day=1)
                else:
                    next_month = date.replace(month=date.month + 1, day=1)
                month_end = next_month - timedelta(days=1)
                if habit.completions.filter(completed_at__date__range=[month_start, month_end]).exists():
                    successful_habits += 1

        success_rate = (successful_habits / total_habits) * 100
        success_rates.append(round(success_rate, 1))

    # Group habits by periodicity
    habits_by_periodicity = {}
    for frequency in Habit.FREQUENCY_CHOICES:
        habits = current_habits.filter(frequency=frequency[0])
        if habits.exists():
            habits_by_periodicity[frequency[1]] = habits
    
    # Calculate overall longest streak across all habits
    longest_overall_span = 0
    for habit in current_habits:
        current_streak = habit.get_current_streak()
        # Convert streak to days based on frequency
        if habit.frequency == 'daily':
            streak_in_days = current_streak
        elif habit.frequency == 'weekly':
            streak_in_days = current_streak * 7
        elif habit.frequency == 'monthly':
            streak_in_days = current_streak * 30  # Approximate month as 30 days
        
        longest_overall_span = max(longest_overall_span, streak_in_days)

    # Calculate current streaks for each habit
    habit_timespans = []
    for habit in current_habits:
        current_streak = habit.get_current_streak()
        habit_timespans.append({
            'habit': habit,
            'timespan': current_streak,
            'first_completion': None,
            'last_completion': None    
        })

    context = {
        'current_habits': current_habits,
        'habits_by_periodicity': habits_by_periodicity,
        'longest_overall_span': longest_overall_span,
        'habit_timespans': sorted(habit_timespans, key=lambda x: x['timespan'], reverse=True),
        'success_rates': json.dumps(success_rates),
        'dates': json.dumps(dates)
    }
    
    return render(request, 'habits/analysis.html', context)
