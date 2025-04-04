from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta, datetime

class Habit(models.Model):
    """
    A model representing a habit that a user wants to track.
    
    This model stores information about habits including their title, description,
    frequency (daily, weekly, or monthly), and timestamps for creation and updates.
    It also provides methods for calculating streak statistics.

    Attributes:
        user (ForeignKey): The user who owns this habit
        title (str): The name of the habit
        description (str): A detailed description of the habit (optional)
        frequency (str): How often the habit should be performed ('daily', 'weekly', or 'monthly')
        created_at (datetime): When the habit was created
        updated_at (datetime): When the habit was last updated
    """

    FREQUENCY_CHOICES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    frequency = models.CharField(max_length=10, choices=FREQUENCY_CHOICES, default='daily')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        """Return a string representation of the habit."""
        return self.title

    class Meta:
        ordering = ['-created_at']

    def get_current_streak(self):
        """
        Calculate the current streak of completed habits.
        
        A streak is considered current if the habit has been completed consistently
        according to its frequency (daily, weekly, or monthly) up until the present day.
        The streak breaks if a required completion is missed.

        Returns:
            int: The number of consecutive times the habit has been completed
                according to its frequency, up to the present day.
        """
        today = timezone.now().date()
        streak = 0
        current_date = today

        while True:
            # Check if there's a completion for the current period
            if self.frequency == 'daily':
                completion = self.completions.filter(
                    completed_at__date=current_date
                ).first()
            elif self.frequency == 'weekly':
                # Check if completed in the week containing this date
                week_start = current_date - timedelta(days=current_date.weekday())
                week_end = week_start + timedelta(days=6)
                completion = self.completions.filter(
                    completed_at__date__range=[week_start, week_end]
                ).first()
            elif self.frequency == 'monthly':
                # Check if completed in the month containing this date
                month_start = current_date.replace(day=1)
                if current_date.month == 12:
                    next_month = current_date.replace(year=current_date.year + 1, month=1, day=1)
                else:
                    next_month = current_date.replace(month=current_date.month + 1, day=1)
                month_end = next_month - timedelta(days=1)
                completion = self.completions.filter(
                    completed_at__date__range=[month_start, month_end]
                ).first()

            if not completion:
                break

            streak += 1
            # Move to the previous day/week/month based on frequency
            if self.frequency == 'daily':
                current_date -= timedelta(days=1)
            elif self.frequency == 'weekly':
                current_date -= timedelta(weeks=1)
            elif self.frequency == 'monthly':
                # Approximate month by subtracting 30 days
                current_date -= timedelta(days=30)

        return streak

    def get_longest_streak(self):
        """
        Calculate the longest streak ever achieved for this habit.
        
        This method analyzes all completions of the habit to find the longest
        streak of consecutive completions according to the habit's frequency.
        A streak is broken if a completion is missed or done on the wrong day.

        Returns:
            int: The length of the longest streak ever achieved for this habit.
                Returns 0 if no completions exist.
        """
        completions = self.completions.order_by('completed_at')
        if not completions:
            return 0

        longest_streak = 1  # Initialize with 1 for the first completion
        current_streak = 1
        previous_date = completions[0].completed_at.date()

        for completion in completions[1:]:
            current_date = completion.completed_at.date()
            
            # Calculate expected date based on frequency
            if self.frequency == 'daily':
                expected_date = previous_date + timedelta(days=1)
            elif self.frequency == 'weekly':
                expected_date = previous_date + timedelta(days=7)
            elif self.frequency == 'monthly':
                expected_date = previous_date + timedelta(days=30)

            if current_date == expected_date:
                current_streak += 1
                longest_streak = max(longest_streak, current_streak)
            else:
                current_streak = 1

            previous_date = current_date

        return longest_streak

    def is_completed_in_current_period(self):
        """
        Check if the habit has been completed in its current period.
        
        For daily habits, checks if completed today.
        For weekly habits, checks if completed in the current week.
        For monthly habits, checks if completed in the current month.

        Returns:
            bool: True if the habit has been completed in its current period,
                 False otherwise.
        """
        now = timezone.now()
        today = now.date()
        
        if self.frequency == 'daily':
            # Check for completions within the current day in user's timezone
            start_of_day = timezone.make_aware(datetime.combine(today, datetime.min.time()))
            end_of_day = timezone.make_aware(datetime.combine(today, datetime.max.time()))
            return self.completions.filter(completed_at__range=(start_of_day, end_of_day)).exists()
        
        elif self.frequency == 'weekly':
            # Get the start of the week (Monday)
            week_start = today - timedelta(days=today.weekday())
            week_end = week_start + timedelta(days=6)
            start_of_week = timezone.make_aware(datetime.combine(week_start, datetime.min.time()))
            end_of_week = timezone.make_aware(datetime.combine(week_end, datetime.max.time()))
            return self.completions.filter(completed_at__range=(start_of_week, end_of_week)).exists()
        
        elif self.frequency == 'monthly':
            # Get the start and end of the current month
            start_of_month = timezone.make_aware(datetime.combine(today.replace(day=1), datetime.min.time()))
            if today.month == 12:
                next_month = today.replace(year=today.year + 1, month=1, day=1)
            else:
                next_month = today.replace(month=today.month + 1, day=1)
            end_of_month = timezone.make_aware(datetime.combine(next_month - timedelta(days=1), datetime.max.time()))
            return self.completions.filter(completed_at__range=(start_of_month, end_of_month)).exists()
        
        return False

class HabitCompletion(models.Model):
    """
    A model representing a single completion of a habit.
    
    This model tracks when a habit was completed and allows for optional notes
    about the completion. It ensures that only one completion per habit per
    timestamp is recorded.

    Attributes:
        habit (ForeignKey): The habit that was completed
        completed_at (datetime): When the habit was completed
        notes (str): Optional notes about the completion
    """

    habit = models.ForeignKey(Habit, on_delete=models.CASCADE, related_name='completions')
    completed_at = models.DateTimeField(default=timezone.now)
    notes = models.TextField(blank=True)

    def __str__(self):
        """Return a string representation of the habit completion."""
        return f"{self.habit.title} completed on {self.completed_at.strftime('%Y-%m-%d')}"

    class Meta:
        ordering = ['-completed_at']
        unique_together = ['habit', 'completed_at']

    def save(self, *args, **kwargs):
        """
        Save the habit completion instance.
        
        This override ensures that the completed_at timestamp is timezone-aware
        before saving the instance to the database.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
        """
        # Ensure completed_at is in the user's timezone
        if not self.completed_at.tzinfo:
            self.completed_at = timezone.make_aware(self.completed_at)
        super().save(*args, **kwargs)
