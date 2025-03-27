
```markdown
# EXPENSE TRACKER
```
The project is hosted at:
https://Anishbh06.pythonanywhere.com.
```

A full-featured Expense Tracker web application built with Django. This project allows users to track one-time and recurring expenses, view income analytics, and even convert currencies—all through a responsive and modern interface.

## Overview

The Expense Tracker project is designed to help users manage their personal finances. Key functionalities include:
- **User Authentication:** Users can register, log in, and view their own data.
- **Expense Tracking:** Log one-time expenses and view them on a dashboard.
- **Recurring Expenses:** Schedule recurring expenses (daily, monthly, yearly) with automatic calculations.
- **Income Tracker:** Track different income sources.
- **Financial Dashboard:** View a summary of income, expenses, recurring expenses, and net income along with interactive charts.
- **Currency Converter:** Convert amounts between different currencies using a live exchange rate API.
- **Responsive Design:** A modern UI built using Material Dashboard and Bootstrap 5 that adapts for both desktop and mobile views.
- **Deployed:** The application is hosted on PythonAnywhere and is accessible from anywhere.

## Features

- **User-Specific Data:** Each user sees only their own financial data.
- **Recurring Expense Calculations:** Automatically calculates recurring expenses based on frequency.
- **Monthly Projections:** Visualize income vs. expenses with Chart.js.
- **Multi-Currency Support:** Convert between various currencies (USD, EUR, INR, GBP, JPY, etc.) with live exchange rates.
- **Flash Messaging:** Instant feedback on actions like logging in, saving an expense, or updating profile information.
- **Responsive Layout:** The UI adapts to different screen sizes with a fixed sidebar for larger screens and an offcanvas menu for mobile.

## Technologies

- **Backend:** Django (Python)
- **Frontend:** HTML, CSS (Material Dashboard, Bootstrap 5), JavaScript (Chart.js)
- **Database:** SQLite (for deployment on PythonAnywhere; can be switched to MySQL locally)
- **Version Control:** Git, hosted on GitHub
- **Deployment:** PythonAnywhere (Free Tier)

## Installation

### Prerequisites

- Python 3.8+ (for local development)
- Git

### Local Setup

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/Anishbh06/Expense-Tracker.git
   cd Expense-Tracker
   ```

2. **Create and Activate a Virtual Environment:**

   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install Requirements:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Apply Migrations:**

   ```bash
   python manage.py migrate
   ```

5. **Collect Static Files:**

   ```bash
   python manage.py collectstatic
   ```

6. **Run the Development Server:**

   ```bash
   python manage.py runserver
   ```

   Visit [http://127.0.0.1:8000](http://127.0.0.1:8000) in your browser.


For a detailed deployment guide, see the [PythonAnywhere documentation]
(https://help.pythonanywhere.com/pages/DeployingDjango/).

## Usage

- **User Registration & Login:** Create an account to track your expenses.
- **Dashboard:** View your monthly summary and interactive charts.
- **Expense & Income Tracking:** Add, edit, and delete expenses and income records.
- **Recurring Expenses:** Schedule expenses that repeat automatically.
- **Currency Converter:** Use the live currency converter to see amounts in different currencies.
- **Profile Management:** Update your profile details and view financial summaries.

## Future Enhancements

- **Automated Testing:** Add unit tests and integration tests.
- **REST API:** Develop RESTful endpoints to allow mobile app integration.
- **Dockerization:** Containerize the application for easier deployment and scalability.
- **Advanced Analytics:** Include more financial insights and data visualizations.


## Contact

For any questions or suggestions, please contact anishbharish@gmail.com

```
