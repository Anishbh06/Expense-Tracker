from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

STATUS_CHOICES = [
    ('active', 'Active'),
    ('inactive', 'Inactive'),
]

class Expense(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.CharField(max_length=255, blank=True, null=True)
    date = models.DateField(default=timezone.now)
    status = models.CharField(max_length=8, choices=STATUS_CHOICES, default='active')

    def __str__(self):
        return f"₹{self.amount} on {self.date}"

class Projection(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    expense_amount = models.DecimalField(max_digits=10, decimal_places=2)
    frequency = models.IntegerField()
    monthly_expense = models.DecimalField(max_digits=12, decimal_places=2)
    yearly_projection = models.DecimalField(max_digits=12, decimal_places=2)
    description = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=8, choices=STATUS_CHOICES, default='active')

    def __str__(self):
        return f"Projection: ₹{self.yearly_projection}"

class RecurringExpense(models.Model):
    FREQUENCY_CHOICES = [
        ('D', 'Daily'),
        ('W', 'Weekly'),
        ('M', 'Monthly'),
        ('Y', 'Yearly'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    frequency = models.CharField(max_length=1, choices=FREQUENCY_CHOICES)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    description = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(max_length=8, choices=STATUS_CHOICES, default='active')
    
    def __str__(self):
        return f"{self.get_frequency_display()} expense of {self.amount}"

        
class Income(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()
    source = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=8, choices=STATUS_CHOICES, default='active')

    def __str__(self):
        return f"{self.source} - {self.amount}"


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    first_name = models.CharField(max_length=30, blank=True, null=True)
    last_name = models.CharField(max_length=30, blank=True, null=True)
    mobile = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Profile for {self.user.username}"