from django.contrib import admin
from django.urls import path, include
from django.contrib.auth.views import LogoutView
from . import views

app_name = 'habits'

# Set the admin site URL to the habit list page
admin.site.site_url = '/'

urlpatterns = [
    path('', views.habit_list, name='habit_list'),
    path('create/', views.habit_create, name='habit_create'),
    path('<int:pk>/', views.habit_detail, name='habit_detail'),
    path('<int:pk>/complete/', views.habit_complete, name='habit_complete'),
    path('<int:pk>/delete/', views.habit_delete, name='habit_delete'),
    path('<int:pk>/edit/', views.habit_edit, name='habit_edit'),
    path('analysis/', views.analysis_dashboard, name='analysis'),
    path('logout/', LogoutView.as_view(next_page='habits:habit_list'), name='logout'),
] 