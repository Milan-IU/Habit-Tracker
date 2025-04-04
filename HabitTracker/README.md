
# Habit Tracker

A Django-based web application for tracking and analyzing your daily habits for my IU Course OOF Programming (DLBDSOOFPP01)

## Features

- Create and manage multiple habits
- Track habit completions
- View detailed statistics and analysis
- Support for daily, weekly, and monthly habits
- Success rate visualization
- Tracking period analysis

## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- Virtual environment

## Installation

1. use Pycharm(my case) or other IDE and Import Project (HabitTracker)

cd HabitTracker


2. Create and activate a virtual environment:

python -m venv venv
venv\Scripts\activate

3. Install the required packages:

django


4. Set up the database:

python manage.py makemigrations
python manage.py migrate

5. Run the development server:

python manage.py runserver


6. Open your web browser and navigate to:

http://127.0.0.1:8000/admin

Enjoy :)