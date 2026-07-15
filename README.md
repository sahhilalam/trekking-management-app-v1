# Trekking Management Application - V2

A role-based web application developed using Flask for managing trekking activities. The application provides separate dashboards for administrators, staff members, and users to efficiently manage treks, bookings, participants, and user accounts.

---

## Features

### Admin
- Dashboard with statistics
- Add, edit and delete treks
- Assign staff to treks
- Approve or blacklist staff
- Approve or blacklist users
- View and search bookings

### Staff
- Dashboard with assigned trek summary
- Manage assigned treks
- Update trek status
- Manage available slots
- View participants
- Cancel participant bookings
- Update profile

### User
- Browse available treks
- Search and filter treks
- Book treks
- Cancel bookings
- View booking history
- Update profile

---

## Tech Stack

- Python 3
- Flask
- SQLAlchemy
- SQLite
- Jinja2
- Bootstrap 5
- HTML
- CSS

---

## Project Structure

```
project/
│
├── app.py
├── models.py
├── admin_routes.py
├── auth_routes.py
├── staff_routes.py
├── user_routes.py
├── requirements.txt
├── README.md
├── project_report.pdf
│
├── templates/
│   ├── admin/
│   ├── staff/
│   ├── user/
│   └── auth/
│
├── static/
│   ├── css/
│   ├── uploads/
│   └── favicon/
│
├── instance/
│
└── venv/
```

---

## Installation

### Clone the repository

```bash
git clone <repository-url>
cd trekking-management-app
```

### Create a virtual environment

**Windows**

```bash
python -m venv venv
```

**macOS/Linux**

```bash
python3 -m venv venv
```

### Activate the virtual environment

**Windows**

```bash
venv\Scripts\activate
```

**macOS/Linux**

```bash
source venv/bin/activate
```

### Install dependencies

```bash
pip install -r requirements.txt
```

---

## Environment Variables

Create a `.env` file in the project root.

```
SECRET_KEY=your_secret_key
SQLALCHEMY_DATABASE_URI=sqlite:///trek.db
UPLOAD_FOLDER=static/uploads/treks
```

---

## Run the application

```bash
python app.py
```

or

```bash
python3 app.py
```

The application will be available at:

```
http://127.0.0.1:5000
```

---

## Default Admin Account

The application automatically creates an administrator account on first run.

Example:

```
Email:
admin@trek.com

Password:
admin123
```

---

## Database

The SQLite database is created automatically when the application is run for the first time.

---

## Author

**Sahil Alam**