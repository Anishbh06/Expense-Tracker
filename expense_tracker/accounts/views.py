import logging
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm  # Add this line
from .forms import SimpleUserCreationForm

logger = logging.getLogger(__name__)

def register(request):
    logger.debug("Register view: method=%s", request.method)
    if request.method == "POST":
        form = SimpleUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            logger.debug("User created: %s", user.username)
            messages.success(request, "Account created successfully. You can now log in.")
            return redirect('login')
        else:
            logger.debug("Registration errors: %s", form.errors)
            messages.error(request, "Registration failed. Please correct the errors below.")
    else:
        form = SimpleUserCreationForm()
        logger.debug("Displaying registration form")

    return render(request, 'accounts/register.html', {'form': form})

def login_view(request):
    logger.debug("Login view called with method: %s", request.method)
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            logger.debug("User logged in: %s", user.username)
            messages.success(request, f"Welcome, {user.username}!")
            return redirect('dashboard')  # Make sure you have a dashboard view and URL
        else:
            logger.debug("Login form errors: %s", form.errors)
            messages.error(request, "Invalid credentials, please try again.")
    else:
        form = AuthenticationForm()
        logger.debug("Displaying login form")
    return render(request, 'accounts/login.html', {'form': form})
