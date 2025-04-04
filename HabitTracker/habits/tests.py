from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from .models import Habit, HabitCompletion

class HabitManagementTests(TestCase):
    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.client.login(username='testuser', password='testpass123')
        
        # Create a test habit
        self.habit = Habit.objects.create(
            user=self.user,
            title='Test Habit',
            description='Test Description',
            frequency='daily'
        )

    def test_habit_creation(self):
        """Test creating a new habit."""
        response = self.client.post(reverse('habits:habit_create'), {
            'title': 'New Habit',
            'description': 'New Description',
            'frequency': 'weekly'
        })
        self.assertEqual(response.status_code, 302)  # Redirect after creation
        self.assertTrue(Habit.objects.filter(title='New Habit').exists())

    def test_habit_edit(self):
        """Test editing an existing habit."""
        response = self.client.post(reverse('habits:habit_edit', args=[self.habit.pk]), {
            'title': 'Updated Habit',
            'description': 'Updated Description',
            'frequency': 'monthly'
        })
        self.assertEqual(response.status_code, 302)  # Redirect after edit
        updated_habit = Habit.objects.get(pk=self.habit.pk)
        self.assertEqual(updated_habit.title, 'Updated Habit')
        self.assertEqual(updated_habit.frequency, 'monthly')

    def test_habit_deletion(self):
        """Test deleting a habit."""
        response = self.client.post(reverse('habits:habit_delete', args=[self.habit.pk]))
        self.assertEqual(response.status_code, 302)  # Redirect after deletion
        self.assertFalse(Habit.objects.filter(pk=self.habit.pk).exists())

class AnalyticsTests(TestCase):
    def setUp(self):
        """Set up test data for analytics."""
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.client.login(username='testuser', password='testpass123')
        
        # Create test habits with different frequencies
        self.daily_habit = Habit.objects.create(
            user=self.user,
            title='Daily Habit',
            frequency='daily'
        )
        self.weekly_habit = Habit.objects.create(
            user=self.user,
            title='Weekly Habit',
            frequency='weekly'
        )
        self.monthly_habit = Habit.objects.create(
            user=self.user,
            title='Monthly Habit',
            frequency='monthly'
        )

        # Create some completions
        today = timezone.now()
        HabitCompletion.objects.create(
            habit=self.daily_habit,
            completed_at=today
        )
        HabitCompletion.objects.create(
            habit=self.weekly_habit,
            completed_at=today
        )
        HabitCompletion.objects.create(
            habit=self.monthly_habit,
            completed_at=today
        )

    def test_current_streak_calculation(self):
        """Test the current streak calculation for different frequencies."""
        # Test daily streak
        self.assertEqual(self.daily_habit.get_current_streak(), 1)
        
        # Test weekly streak
        self.assertEqual(self.weekly_habit.get_current_streak(), 1)
        
        # Test monthly streak
        self.assertEqual(self.monthly_habit.get_current_streak(), 1)

    def test_longest_streak_calculation(self):
        """Test the longest streak calculation."""
        # First, delete the initial completion from setUp
        self.daily_habit.completions.all().delete()
        
        # Create completions in chronological order (oldest to newest)
        today = timezone.now()
        for i in range(5, -1, -1):  # Count down from 5 to 0
            HabitCompletion.objects.create(
                habit=self.daily_habit,
                completed_at=today - timedelta(days=i)
            )
        
        # Verify the completions are in the correct order
        completions = self.daily_habit.completions.order_by('completed_at')
        self.assertEqual(len(completions), 6)  # Should have 6 consecutive completions
        
        # Check the longest streak
        self.assertEqual(self.daily_habit.get_longest_streak(), 6)

    def test_is_completed_in_current_period(self):
        """Test checking if a habit is completed in its current period."""
        # Test daily habit
        self.assertTrue(self.daily_habit.is_completed_in_current_period())
        
        # Test weekly habit
        self.assertTrue(self.weekly_habit.is_completed_in_current_period())
        
        # Test monthly habit
        self.assertTrue(self.monthly_habit.is_completed_in_current_period())

    def test_analysis_dashboard_view(self):
        """Test the analysis dashboard view."""
        response = self.client.get(reverse('habits:analysis'))
        self.assertEqual(response.status_code, 200)
        
        # Check if the context contains necessary data
        self.assertIn('current_habits', response.context)
        self.assertIn('habits_by_periodicity', response.context)
        self.assertIn('longest_overall_span', response.context)
        self.assertIn('habit_timespans', response.context)
        self.assertIn('success_rates', response.context)
        self.assertIn('dates', response.context)

    def test_success_rate_calculation(self):
        """Test the success rate calculation in the analysis dashboard."""
        # Add more completions to test success rate
        for i in range(3):
            HabitCompletion.objects.get_or_create(
                habit=self.daily_habit,
                completed_at=timezone.now() - timedelta(days=i)
            )
        
        response = self.client.get(reverse('habits:analysis'))
        self.assertEqual(response.status_code, 200)
        
        # Check if success rates are calculated
        success_rates = response.context['success_rates']
        self.assertIsNotNone(success_rates)
        self.assertTrue(len(success_rates) > 0)
