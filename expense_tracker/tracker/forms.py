# tracker/forms.py
from django import forms
from .models import Expense, Projection, RecurringExpense, Income, UserProfile

class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ['amount', 'description', 'date']

class ProjectionForm(forms.ModelForm):
    class Meta:
        model = Projection
        # We only need the input fields; monthly_expense and yearly_projection are calculated.
        fields = ['expense_amount', 'frequency', 'description']

class RecurringExpenseForm(forms.ModelForm):
    start_date = forms.DateField(required=False)
    end_date = forms.DateField(required=False)
    
    class Meta:
        model = RecurringExpense
        fields = ['amount', 'frequency', 'start_date', 'end_date', 'description', 'status']


class IncomeForm(forms.ModelForm):
    class Meta:
        model = Income
        fields = ['date', 'source', 'amount', 'description']

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['first_name', 'last_name', 'mobile', 'address']
