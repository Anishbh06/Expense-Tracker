from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('expenses/', views.expense_tracking, name='expense_tracking'),
    path('expenses/edit/<int:pk>/', views.edit_expense, name='edit_expense'),
    path('expenses/delete/<int:pk>/', views.delete_expense, name='delete_expense'),
    path('yearly-projection/', views.yearly_projection, name='yearly_projection'),
    path('edit-projection/', views.edit_projection, name='edit_projection'),
    path('delete-projection/<int:proj_id>/', views.delete_projection, name='delete_projection'),
    path('recurring-expense/', views.recurring_expense, name='recurring_expense'),
    path('recurring-expense/edit/<int:pk>/', views.edit_recurring_expense, name='edit_recurring_expense'),
    path('recurring-expense/delete/<int:pk>/', views.delete_recurring_expense, name='delete_recurring_expense'),
    path('income/', views.income_tracking, name='income_tracking'),
    path('income/edit/<int:pk>/', views.edit_income, name='edit_income'),
    path('income/delete/<int:pk>/', views.delete_income, name='delete_income'),
    path('profile/', views.profile, name='profile'),  # Added Profile route
    path('profile/edit/', views.edit_profile, name='edit_profile'),


]
