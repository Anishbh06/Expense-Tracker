import calendar
import datetime
from datetime import date, timedelta
import requests  # Ensure you have installed this package
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Sum
from django.db.models.functions import TruncMonth
from django.contrib.auth.decorators import login_required
from .models import Expense, Projection, RecurringExpense, Income, UserProfile
from .forms import ExpenseForm, ProjectionForm, RecurringExpenseForm, IncomeForm, UserProfileForm

@login_required
def dashboard(request):
    # Define current month boundaries
    today = date.today()
    first_day = date(today.year, today.month, 1)
    last_day = date(today.year, today.month, calendar.monthrange(today.year, today.month)[1])
    
    # Total Income and Expenses for the CURRENT month
    total_income = Income.objects.filter(
        user=request.user,
        status='active',
        date__gte=first_day,
        date__lte=last_day
    ).aggregate(total=Sum('amount'))['total'] or 0

    total_expenses = Expense.objects.filter(
        user=request.user,
        status='active',
        date__gte=first_day,
        date__lte=last_day
    ).aggregate(total=Sum('amount'))['total'] or 0

    # Calculate recurring expense total for the CURRENT month (for summary card)
    total_recurring_calculated = 0
    recurring_qs = RecurringExpense.objects.filter(user=request.user, status='active')
    for rec in recurring_qs:
        if rec.frequency == 'D':
            effective_start = rec.start_date if rec.start_date else first_day
            effective_end = rec.end_date if rec.end_date else last_day
            start_calc = max(effective_start, first_day)
            end_calc = min(effective_end, last_day)
            if start_calc <= end_calc:
                num_days = (end_calc - start_calc).days + 1
            else:
                num_days = 0
            total_recurring_calculated += rec.amount * num_days
        elif rec.frequency == 'M':
            effective_start = rec.start_date if rec.start_date else first_day
            if effective_start <= last_day and (rec.end_date is None or rec.end_date >= first_day):
                total_recurring_calculated += rec.amount
        elif rec.frequency == 'Y':
            if rec.start_date:
                if today >= rec.start_date + timedelta(days=365):
                    if rec.start_date <= last_day and (rec.end_date is None or rec.end_date >= first_day):
                        total_recurring_calculated += rec.amount
            else:
                total_recurring_calculated += rec.amount

    total_recurring = total_recurring_calculated

    # Net Income for current month
    net_income = total_income - total_expenses - total_recurring

    # Prepare monthly chart data for one-time incomes and expenses for the entire year
    current_year = today.year
    income_data_qs = Income.objects.filter(user=request.user, status='active', date__year=current_year)\
                           .annotate(month=TruncMonth('date'))\
                           .values('month')\
                           .annotate(total=Sum('amount'))\
                           .order_by('month')
    expense_data_qs = Expense.objects.filter(user=request.user, status='active', date__year=current_year)\
                            .annotate(month=TruncMonth('date'))\
                            .values('month')\
                            .annotate(total=Sum('amount'))\
                            .order_by('month')
    months = [calendar.month_name[i] for i in range(1, 13)]
    income_data_dict = {entry['month'].strftime('%B'): entry['total'] for entry in income_data_qs}
    expense_data_dict = {entry['month'].strftime('%B'): entry['total'] for entry in expense_data_qs}
    income_chart = [float(income_data_dict.get(month, 0)) for month in months]
    expense_chart = [float(expense_data_dict.get(month, 0)) for month in months]

    # Helper function: calculate recurring expense total for a given month
    def recurring_for_month(user, year, month):
        first_day_of_month = date(year, month, 1)
        last_day_of_month = date(year, month, calendar.monthrange(year, month)[1])
        total = 0
        recurring_qs = RecurringExpense.objects.filter(user=user, status='active')
        for rec in recurring_qs:
            if rec.frequency == 'D':
                effective_start = rec.start_date if rec.start_date else first_day_of_month
                effective_end = rec.end_date if rec.end_date else last_day_of_month
                start_calc = max(effective_start, first_day_of_month)
                end_calc = min(effective_end, last_day_of_month)
                if start_calc <= end_calc:
                    num_days = (end_calc - start_calc).days + 1
                else:
                    num_days = 0
                total += rec.amount * num_days
            elif rec.frequency == 'M':
                effective_start = rec.start_date if rec.start_date else first_day_of_month
                if effective_start <= last_day_of_month and (rec.end_date is None or rec.end_date >= first_day_of_month):
                    total += rec.amount
            elif rec.frequency == 'Y':
                if rec.start_date:
                    if first_day_of_month >= rec.start_date + timedelta(days=365):
                        if rec.start_date <= last_day_of_month and (rec.end_date is None or rec.end_date >= first_day_of_month):
                            total += rec.amount
                else:
                    total += rec.amount
        return total

    recurring_chart = [float(recurring_for_month(request.user, current_year, m)) for m in range(1, 13)]

    # --- Multi-Currency Conversion ---
    conversion_result = None
    conversion_amount = None
    from_currency = None
    to_currency = None

    currencies_dict = {
        "USD": {"name": "US Dollar", "symbol": "$"},
        "EUR": {"name": "Euro", "symbol": "€"},
        "INR": {"name": "Indian Rupee", "symbol": "₹"},
        "GBP": {"name": "British Pound", "symbol": "£"},
        "JPY": {"name": "Japanese Yen", "symbol": "¥"},
        "AUD": {"name": "Australian Dollar", "symbol": "A$"},
        "CAD": {"name": "Canadian Dollar", "symbol": "C$"},
        "CHF": {"name": "Swiss Franc", "symbol": "CHF"},
        "CNY": {"name": "Chinese Yuan", "symbol": "¥"}
    }

    if request.method == "POST" and "convert_currency" in request.POST:
        from_currency = request.POST.get("from_currency")
        to_currency = request.POST.get("to_currency")
        conversion_amount = request.POST.get("conversion_amount")
        try:
            conversion_amount = float(conversion_amount)
            api_url = f"https://api.exchangerate-api.com/v4/latest/{from_currency}"
            response = requests.get(api_url)
            data = response.json()
            if "rates" in data and to_currency in data["rates"]:
                rate = data["rates"][to_currency]
                conversion_result = conversion_amount * rate
            else:
                conversion_result = "Conversion rate not available."
        except Exception as e:
            conversion_result = f"Error: {str(e)}"

    current_month = today.strftime("%B")

    context = {
        'total_income': total_income,
        'total_expenses': total_expenses,
        'total_recurring': total_recurring,
        'net_income': net_income,
        'chart_labels': months,
        'income_data': income_chart,
        'expense_data': expense_chart,
        'recurring_data': recurring_chart,
        # Currency conversion context
        'conversion_result': conversion_result,
        'conversion_amount': conversion_amount,
        'from_currency': from_currency,
        'to_currency': to_currency,
        'currencies': currencies_dict,
        'current_month': current_month,
    }
    return render(request, 'tracker/dashboard.html', context)


@login_required
def expense_tracking(request):
    if request.method == "POST":
        form = ExpenseForm(request.POST)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.user = request.user
            expense.save()
            messages.success(request, "Expense record added successfully.")
            return redirect('expense_tracking')
    else:
        form = ExpenseForm()

    expenses = Expense.objects.filter(user=request.user, status='active').order_by('-date')
    return render(request, 'tracker/expense.html', {
        'form': form,
        'expenses': expenses,
    })

@login_required
def edit_expense(request, pk):
    expense = get_object_or_404(Expense, pk=pk, user=request.user, status='active')
    if request.method == "POST":
        form = ExpenseForm(request.POST, instance=expense)
        if form.is_valid():
            form.save()
            messages.success(request, "Expense record updated successfully.")
            return redirect('expense_tracking')
    else:
        form = ExpenseForm(instance=expense)
    return render(request, 'tracker/edit_expense.html', {'form': form, 'expense': expense})

@login_required
def delete_expense(request, pk):
    expense = get_object_or_404(Expense, pk=pk, user=request.user, status='active')
    if request.method == "POST":
        expense.delete()
        messages.success(request, "Expense record deleted successfully.")
    return redirect('expense_tracking')

@login_required
def yearly_projection(request):
    projection_result = None
    expense_amount = None
    frequency = None
    form = ProjectionForm()

    if request.method == 'POST':
        form = ProjectionForm(request.POST)
        if form.is_valid():
            expense_amount = form.cleaned_data['expense_amount']
            frequency = form.cleaned_data['frequency']
            description = form.cleaned_data.get('description', '')
            monthly_expense = expense_amount * frequency
            projection_result = monthly_expense * 12

            if "save" in request.POST:
                Projection.objects.create(
                    user=request.user,
                    expense_amount=expense_amount,
                    frequency=frequency,
                    monthly_expense=monthly_expense,
                    yearly_projection=projection_result,
                    description=description
                )
                messages.success(request, "Projection saved successfully!")
                return redirect("yearly_projection")
            elif "calculate" in request.POST:
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    return JsonResponse({
                        'expense_amount': str(expense_amount),
                        'frequency': str(frequency),
                        'projection_result': str(projection_result),
                    })
    else:
        form = ProjectionForm()

    all_projections = Projection.objects.filter(user=request.user, status='active').order_by('-created_at')
    context = {
        'form': form,
        'projection_result': projection_result,
        'expense_amount': expense_amount,
        'frequency': frequency,
        'projections': all_projections,
    }
    return render(request, 'tracker/yearly_projection.html', context)

@login_required
def edit_projection(request):
    if request.method == "POST":
        proj_id = request.POST.get("projection_id")
        projection = get_object_or_404(Projection, id=proj_id, user=request.user, status='active')
        form = ProjectionForm(request.POST, instance=projection)
        if form.is_valid():
            expense_amount = form.cleaned_data['expense_amount']
            frequency = form.cleaned_data['frequency']
            description = form.cleaned_data.get('description', '')
            monthly_expense = expense_amount * frequency
            projection = form.save(commit=False)
            projection.monthly_expense = monthly_expense
            projection.yearly_projection = monthly_expense * 12
            projection.save()
            messages.success(request, "Projection updated successfully!")
            return redirect("yearly_projection")
        else:
            messages.error(request, "Failed to update projection. Please try again.")
    return redirect("yearly_projection")

@login_required
def delete_projection(request, proj_id):
    projection = get_object_or_404(Projection, id=proj_id, user=request.user, status='active')
    if request.method == "POST":
        projection.delete()
        messages.success(request, "Projection deleted successfully!")
    return redirect("yearly_projection")

@login_required
def recurring_expense(request):
    if request.method == "POST":
        form = RecurringExpenseForm(request.POST)
        if form.is_valid():
            recurring_exp = form.save(commit=False)
            recurring_exp.user = request.user
            recurring_exp.save()
            messages.success(request, "Recurring expense added successfully.")
            return redirect('recurring_expense')
    else:
        form = RecurringExpenseForm()

    recurring_expenses = RecurringExpense.objects.filter(user=request.user).order_by('-id')
    # Pass status choices for use in the template
    status_choices = RecurringExpense._meta.get_field('status').choices
    return render(request, 'tracker/recurring_expense.html', {
        'form': form,
        'recurring_expenses': recurring_expenses,
        'status_choices': status_choices,
    })


@login_required
def edit_recurring_expense(request, pk):
    recurring_exp = get_object_or_404(RecurringExpense, pk=pk, user=request.user)
    if request.method == "POST":
        form = RecurringExpenseForm(request.POST, instance=recurring_exp)
        if form.is_valid():
            form.save()
            messages.success(request, "Recurring expense updated successfully.")
            return redirect('recurring_expense')
    else:
        form = RecurringExpenseForm(instance=recurring_exp)
    return render(request, 'tracker/edit_recurring_expense.html', {'form': form})

@login_required
def delete_recurring_expense(request, pk):
    recurring_exp = get_object_or_404(RecurringExpense, pk=pk, user=request.user)
    if request.method == "POST":
        recurring_exp.delete()
        messages.success(request, "Recurring expense deleted successfully.")
    return redirect('recurring_expense')

@login_required
def income_tracking(request):
    if request.method == "POST":
        form = IncomeForm(request.POST)
        if form.is_valid():
            income = form.save(commit=False)
            income.user = request.user
            income.save()
            messages.success(request, "Income record added successfully.")
            return redirect('income_tracking')
    else:
        form = IncomeForm()

    incomes = Income.objects.filter(user=request.user, status='active').order_by('-date')
    return render(request, 'tracker/income.html', {
        'form': form,
        'incomes': incomes,
    })

@login_required
def edit_income(request, pk):
    income = get_object_or_404(Income, pk=pk, user=request.user, status='active')
    if request.method == "POST":
        form = IncomeForm(request.POST, instance=income)
        if form.is_valid():
            form.save()
            messages.success(request, "Income record updated successfully.")
            return redirect('income_tracking')
    else:
        form = IncomeForm(instance=income)
    return render(request, 'tracker/edit_income.html', {'form': form, 'income': income})

@login_required
def delete_income(request, pk):
    income = get_object_or_404(Income, pk=pk, user=request.user, status='active')
    if request.method == "POST":
        income.delete()
        messages.success(request, "Income record deleted successfully.")
    return redirect('income_tracking')


@login_required
def profile(request):
    user = request.user

    # Define current month boundaries
    today = date.today()
    first_day = date(today.year, today.month, 1)
    last_day = date(today.year, today.month, calendar.monthrange(today.year, today.month)[1])

    # Calculate current month totals
    total_income = Income.objects.filter(
        user=user, status='active', date__gte=first_day, date__lte=last_day
    ).aggregate(total=Sum('amount'))['total'] or 0

    total_expenses = Expense.objects.filter(
        user=user, status='active', date__gte=first_day, date__lte=last_day
    ).aggregate(total=Sum('amount'))['total'] or 0

    # Recurring expenses for current month
    total_recurring_calculated = 0
    recurring_qs = RecurringExpense.objects.filter(user=user, status='active')
    for rec in recurring_qs:
        if rec.frequency == 'D':
            effective_start = rec.start_date if rec.start_date else first_day
            effective_end = rec.end_date if rec.end_date else last_day
            start_calc = max(effective_start, first_day)
            end_calc = min(effective_end, last_day)
            if start_calc <= end_calc:
                num_days = (end_calc - start_calc).days + 1
            else:
                num_days = 0
            total_recurring_calculated += rec.amount * num_days
        elif rec.frequency == 'M':
            effective_start = rec.start_date if rec.start_date else first_day
            if effective_start <= last_day and (rec.end_date is None or rec.end_date >= first_day):
                total_recurring_calculated += rec.amount
        elif rec.frequency == 'Y':
            if rec.start_date:
                if today >= rec.start_date + timedelta(days=365):
                    if rec.start_date <= last_day and (rec.end_date is None or rec.end_date >= first_day):
                        total_recurring_calculated += rec.amount
            else:
                total_recurring_calculated += rec.amount
    total_recurring = total_recurring_calculated

    net_income = total_income - total_expenses - total_recurring
    current_month = today.strftime("%B")

    context = {
        'user': user,
        'total_income': total_income,
        'total_expenses': total_expenses,
        'total_recurring': total_recurring,
        'net_income': net_income,
        'current_month': current_month,
    }
    return render(request, 'tracker/profile.html', context)


@login_required
def edit_profile(request):
    try:
        profile = request.user.profile
    except Exception:
        # Create new profile if it doesn't exist
        profile = UserProfile(user=request.user)
    
    if request.method == "POST":
        form = UserProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect('profile')
        else:
            messages.error(request, "There were errors updating your profile.")
    else:
        form = UserProfileForm(instance=profile)
        
    return render(request, 'tracker/profile.html', {'form': form, 'edit_mode': True})