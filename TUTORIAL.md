# 📚 Building a Flask App from Zero - Step by Step Tutorial

## Table of Contents
1. [Understanding the Project Structure](#understanding-the-project-structure)
2. [Prerequisites](#prerequisites)
3. [Step-by-Step Build Process](#step-by-step-build-process)
4. [Understanding Each Component](#understanding-each-component)
5. [Testing and Deployment](#testing-and-deployment)

---

## Understanding the Project Structure

Before we start, let's understand what we're building:

```
apartment-reservation-manager/
├── app.py                          # Main application (backend logic)
├── requirements.txt                # Python dependencies
├── reservations.db                 # Database (auto-created)
├── templates/                      # HTML templates (frontend)
│   ├── base.html                  # Base layout
│   ├── index.html                 # Dashboard page
│   ├── add_reservation.html       # Add form
│   ├── edit_reservation.html      # Edit form
│   ├── calendar.html              # Timeline view
│   └── readonly_login.html        # Cleaning crew login
└── static/                         # Static files (CSS, images)
    └── css/
        └── style.css              # Styling
```

---

## Prerequisites

**What you need to know:**
- Basic Python syntax (variables, functions, loops)
- Basic HTML (tags, forms)
- Basic CSS (selectors, properties)
- How to use terminal/command line

**What Flask is:**
- Flask is a Python web framework
- It helps you create websites and web applications
- Think of it as a tool that connects your Python code to web pages

---

## Step-by-Step Build Process

### STEP 1: Set Up Your Environment

#### 1.1 Create Project Folder
```bash
# In terminal/Codespace
mkdir apartment-reservation-manager
cd apartment-reservation-manager
```

**What this does:** Creates a folder for your project and moves into it.

#### 1.2 Create Virtual Environment (Optional but recommended)
```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate
```

**What this does:** Creates an isolated Python environment for your project.

#### 1.3 Create requirements.txt
Create a file named `requirements.txt` and add:
```
Flask==3.0.0
Flask-SQLAlchemy==3.1.1
```

**What this does:** Lists all Python packages your app needs.

#### 1.4 Install Dependencies
```bash
pip install -r requirements.txt
```

**What this does:** Downloads and installs Flask and database tools.

---

### STEP 2: Create the Database Model (app.py - Part 1)

Create `app.py` and start with imports:

```python
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date
from functools import wraps
import os
```

**What each import does:**
- `Flask`: Main application class
- `render_template`: Displays HTML pages
- `request`: Gets data from forms
- `redirect`: Sends user to another page
- `url_for`: Creates URLs for routes
- `flash`: Shows temporary messages
- `jsonify`: Converts Python data to JSON
- `session`: Stores user session data
- `SQLAlchemy`: Database manager
- `datetime, date`: Handles dates
- `wraps`: Helps create decorators
- `os`: Accesses environment variables

#### 2.1 Initialize Flask App
```python
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-change-this'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///reservations.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

READONLY_PASSWORD = os.environ.get('READONLY_PASSWORD', 'cleaning123')

db = SQLAlchemy(app)
```

**What this does:**
- Creates Flask application
- `SECRET_KEY`: Secures sessions and forms
- `SQLALCHEMY_DATABASE_URI`: Tells Flask where to store data (SQLite file)
- `READONLY_PASSWORD`: Password for cleaning crew
- `db`: Database manager object

#### 2.2 Create Database Model
```python
class Reservation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    guest_name = db.Column(db.String(100), nullable=False)
    platform = db.Column(db.String(20), nullable=False)
    check_in = db.Column(db.Date, nullable=False)
    check_out = db.Column(db.Date, nullable=False)
    adults = db.Column(db.Integer, default=1)
    children = db.Column(db.Integer, default=0)
    special_requests = db.Column(db.Text)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'guest_name': self.guest_name,
            'platform': self.platform,
            'check_in': self.check_in.isoformat(),
            'check_out': self.check_out.isoformat(),
            'adults': self.adults,
            'children': self.children,
            'special_requests': self.special_requests,
            'notes': self.notes
        }
```

**What this does:**
- Defines the structure of a reservation in the database
- Like creating a table with columns in Excel
- `id`: Unique number for each reservation
- `db.Column`: Defines each field/column
- `db.Integer`: Number type
- `db.String(100)`: Text up to 100 characters
- `db.Date`: Date type
- `db.Text`: Long text
- `nullable=False`: Field is required
- `default=1`: Default value if not provided
- `to_dict()`: Converts reservation to dictionary (useful for API)

---

### STEP 3: Create Routes (app.py - Part 2)

Routes are URLs that users can visit. Each route has a function that runs when visited.

#### 3.1 Create Read-Only Decorator
```python
def check_readonly(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('readonly_mode'):
            flash('You are in read-only mode. You cannot modify reservations.', 'error')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function
```

**What this does:**
- Creates a reusable function that checks if user is in read-only mode
- If yes, blocks them from editing/adding/deleting
- Decorators wrap functions to add extra behavior

#### 3.2 Home Page Route
```python
@app.route('/')
def index():
    reservations = Reservation.query.order_by(Reservation.check_in).all()
    is_readonly = session.get('readonly_mode', False)
    return render_template('index.html', reservations=reservations, is_readonly=is_readonly)
```

**What this does:**
- `@app.route('/')`: When user visits homepage
- `Reservation.query.order_by()`: Gets all reservations from database, sorted by check-in date
- `session.get('readonly_mode')`: Checks if user is in read-only mode
- `render_template()`: Shows the HTML page, passing data to it

#### 3.3 Read-Only Login Route
```python
@app.route('/readonly-login', methods=['GET', 'POST'])
def readonly_login():
    if request.method == 'POST':
        password = request.form.get('password')
        if password == READONLY_PASSWORD:
            session['readonly_mode'] = True
            flash('Logged in as read-only user (Cleaning Crew)', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid password', 'error')
    return render_template('readonly_login.html')
```

**What this does:**
- `methods=['GET', 'POST']`: Accepts both viewing the page (GET) and form submission (POST)
- `request.method == 'POST'`: Checks if form was submitted
- `request.form.get('password')`: Gets password from form
- Compares password with correct one
- `session['readonly_mode'] = True`: Marks user as read-only
- `flash()`: Shows success or error message

#### 3.4 Add Reservation Route
```python
@app.route('/add', methods=['GET', 'POST'])
@check_readonly
def add_reservation():
    if request.method == 'POST':
        try:
            reservation = Reservation(
                guest_name=request.form['guest_name'],
                platform=request.form['platform'],
                check_in=datetime.strptime(request.form['check_in'], '%Y-%m-%d').date(),
                check_out=datetime.strptime(request.form['check_out'], '%Y-%m-%d').date(),
                adults=int(request.form['adults']),
                children=int(request.form['children']),
                special_requests=request.form.get('special_requests', ''),
                notes=request.form.get('notes', '')
            )
            
            if reservation.check_out <= reservation.check_in:
                flash('Check-out date must be after check-in date!', 'error')
                return redirect(url_for('add_reservation'))
            
            db.session.add(reservation)
            db.session.commit()
            flash('Reservation added successfully!', 'success')
            return redirect(url_for('index'))
        except Exception as e:
            flash(f'Error adding reservation: {str(e)}', 'error')
            return redirect(url_for('add_reservation'))
    
    return render_template('add_reservation.html')
```

**What this does:**
- `@check_readonly`: Blocks if in read-only mode
- Gets all form data
- `datetime.strptime()`: Converts text date to date object
- `int()`: Converts text to number
- Validates check-out is after check-in
- `db.session.add()`: Adds to database
- `db.session.commit()`: Saves changes
- `try/except`: Catches errors gracefully

#### 3.5 Edit and Delete Routes
```python
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
@check_readonly
def edit_reservation(id):
    reservation = Reservation.query.get_or_404(id)
    
    if request.method == 'POST':
        # Similar to add, but updates existing reservation
        reservation.guest_name = request.form['guest_name']
        # ... update other fields ...
        db.session.commit()
        flash('Reservation updated successfully!', 'success')
        return redirect(url_for('index'))
    
    return render_template('edit_reservation.html', reservation=reservation)

@app.route('/delete/<int:id>')
@check_readonly
def delete_reservation(id):
    reservation = Reservation.query.get_or_404(id)
    db.session.delete(reservation)
    db.session.commit()
    flash('Reservation deleted successfully!', 'success')
    return redirect(url_for('index'))
```

**What this does:**
- `<int:id>`: Takes ID from URL (e.g., /edit/5)
- `get_or_404()`: Gets reservation or shows 404 error if not found
- `db.session.delete()`: Removes from database

#### 3.6 Run the App
```python
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5000)
```

**What this does:**
- `if __name__ == '__main__'`: Only runs when you directly run this file
- `db.create_all()`: Creates database tables
- `app.run()`: Starts the web server
- `debug=True`: Shows helpful error messages
- `host='0.0.0.0'`: Makes it accessible from other devices
- `port=5000`: Runs on port 5000

---

### STEP 4: Create HTML Templates

Templates are HTML files with special placeholders for dynamic data.

#### 4.1 Create templates Folder
```bash
mkdir templates
```

#### 4.2 Create base.html (Master Template)

This is the main layout that all pages inherit from:

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}Reservation Manager{% endblock %}</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
</head>
<body>
    <nav class="navbar">
        <div class="container">
            <h1>🏠 Apartment Reservation Manager</h1>
            <ul class="nav-links">
                <li><a href="{{ url_for('index') }}">Dashboard</a></li>
                <li><a href="{{ url_for('calendar_view') }}">Calendar</a></li>
                
                {% if not is_readonly is defined or not is_readonly %}
                <li><a href="{{ url_for('add_reservation') }}" class="btn-primary">+ Add Reservation</a></li>
                {% endif %}
                
                {% if is_readonly is defined and is_readonly %}
                <li><span class="readonly-badge">👁️ Read-Only Mode</span></li>
                <li><a href="{{ url_for('exit_readonly') }}" class="btn-secondary">Exit</a></li>
                {% else %}
                <li><a href="{{ url_for('readonly_login') }}" class="btn-secondary">🔒 Cleaning Crew Access</a></li>
                {% endif %}
            </ul>
        </div>
    </nav>

    <div class="container">
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                    <div class="alert alert-{{ category }}">
                        {{ message }}
                    </div>
                {% endfor %}
            {% endif %}
        {% endwith %}

        {% block content %}{% endblock %}
    </div>

    <footer>
        <div class="container">
            <p>&copy; 2024 Apartment Reservation Manager</p>
        </div>
    </footer>
</body>
</html>
```

**What Jinja2 syntax means:**
- `{% block title %}`: Placeholder for page title
- `{{ url_for('index') }}`: Generates URL for index route
- `{% if %}`: Conditional statement
- `{% for %}`: Loop
- `{{ variable }}`: Outputs variable value

#### 4.3 Create index.html (Dashboard)

```html
{% extends "base.html" %}

{% block title %}Dashboard{% endblock %}

{% block content %}
<div class="dashboard">
    <h2>Reservations Overview</h2>
    
    {% if reservations %}
        <table>
            <thead>
                <tr>
                    <th>Guest Name</th>
                    <th>Platform</th>
                    <th>Check-in</th>
                    <th>Check-out</th>
                    <th>Guests</th>
                    {% if not is_readonly %}
                    <th>Actions</th>
                    {% endif %}
                </tr>
            </thead>
            <tbody>
                {% for reservation in reservations %}
                <tr>
                    <td>{{ reservation.guest_name }}</td>
                    <td>{{ reservation.platform }}</td>
                    <td>{{ reservation.check_in }}</td>
                    <td>{{ reservation.check_out }}</td>
                    <td>{{ reservation.adults }} adults</td>
                    {% if not is_readonly %}
                    <td>
                        <a href="{{ url_for('edit_reservation', id=reservation.id) }}">Edit</a>
                        <a href="{{ url_for('delete_reservation', id=reservation.id) }}">Delete</a>
                    </td>
                    {% endif %}
                </tr>
                {% endfor %}
            </tbody>
        </table>
    {% else %}
        <p>No reservations yet.</p>
    {% endif %}
</div>
{% endblock %}
```

**What this does:**
- `{% extends "base.html" %}`: Uses base template
- Loops through reservations and displays each in table row
- Conditionally shows Edit/Delete buttons

#### 4.4 Create Form Templates

Similar structure for `add_reservation.html` and `edit_reservation.html`:

```html
{% extends "base.html" %}

{% block content %}
<form method="POST">
    <input type="text" name="guest_name" required>
    <select name="platform" required>
        <option value="airbnb">Airbnb</option>
        <option value="booking">Booking.com</option>
    </select>
    <input type="date" name="check_in" required>
    <input type="date" name="check_out" required>
    <button type="submit">Add Reservation</button>
</form>
{% endblock %}
```

**HTML Form Elements:**
- `method="POST"`: Submits data to server
- `name="guest_name"`: Name Flask uses to get data
- `required`: Browser enforces this field
- `type="date"`: Shows date picker

---

### STEP 5: Add Styling (CSS)

#### 5.1 Create static Folder
```bash
mkdir -p static/css
```

#### 5.2 Create style.css

CSS controls how things look:

```css
body {
    font-family: Arial, sans-serif;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    margin: 0;
    padding: 0;
}

.navbar {
    background: white;
    padding: 1rem;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

.container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
}

table {
    width: 100%;
    background: white;
    border-collapse: collapse;
}

th, td {
    padding: 12px;
    border-bottom: 1px solid #ddd;
    text-align: left;
}

.btn-primary {
    background: #667eea;
    color: white;
    padding: 10px 20px;
    border: none;
    border-radius: 5px;
    cursor: pointer;
}

.readonly-badge {
    background: #ffc107;
    color: #333;
    padding: 8px 16px;
    border-radius: 5px;
    font-weight: bold;
}
```

**CSS Concepts:**
- Selector (e.g., `.navbar`): Targets HTML elements
- Property (e.g., `background`): What to style
- Value (e.g., `white`): How to style it

---

### STEP 6: Run and Test

#### 6.1 Start the Server
```bash
python app.py
```

#### 6.2 Open in Browser
- Go to `http://localhost:5000`
- Or in Codespaces, click "Open in Browser" when prompted

#### 6.3 Test Features
1. Add a reservation
2. View it in dashboard
3. Edit it
4. Check calendar view
5. Login as cleaning crew (password: cleaning123)
6. Verify you can't edit in read-only mode

---

## Understanding Each Component

### How Flask Routes Work

```
User types URL → Flask finds matching route → Function runs → Returns HTML
```

Example:
```
User: http://localhost:5000/add
Flask: Found @app.route('/add')
Flask: Runs add_reservation() function
Function: Returns add_reservation.html template
Browser: Displays the page
```

### How Forms Work

```
1. User sees form (GET request)
2. User fills form and clicks Submit
3. Browser sends data (POST request)
4. Flask receives data in request.form
5. Flask processes and saves to database
6. Flask redirects to another page
```

### How Database Works

```
1. Define model (Reservation class)
2. Create tables (db.create_all())
3. Add data (db.session.add())
4. Save changes (db.session.commit())
5. Query data (Reservation.query.all())
```

### How Templates Work

```
1. Flask calls render_template('index.html', data=data)
2. Jinja2 processes template
3. Replaces {{ variable }} with actual values
4. Evaluates {% if %} and {% for %}
5. Returns final HTML to browser
```

---

## Common Issues and Solutions

### Issue 1: Module Not Found
**Error:** `ModuleNotFoundError: No module named 'flask'`
**Solution:** 
```bash
pip install -r requirements.txt
```

### Issue 2: Database Locked
**Error:** `database is locked`
**Solution:** Close other programs using the database, or restart the app

### Issue 3: Port Already in Use
**Error:** `Address already in use`
**Solution:** 
```bash
# Kill process on port 5000
lsof -ti:5000 | xargs kill -9
# Or use different port
app.run(port=5001)
```

### Issue 4: Template Not Found
**Error:** `TemplateNotFound: index.html`
**Solution:** Make sure templates folder exists and contains the HTML file

---

## Next Steps

1. **Add more features:**
   - Export to Excel
   - Email notifications
   - Calendar integration
   - Photo uploads

2. **Improve security:**
   - Change SECRET_KEY to random value
   - Use environment variables
   - Add user authentication

3. **Deploy online:**
   - Use Heroku, PythonAnywhere, or Render
   - Set up proper database (PostgreSQL)
   - Use production server (Gunicorn)

4. **Learn more:**
   - Flask documentation: https://flask.palletsprojects.com/
   - SQLAlchemy: https://www.sqlalchemy.org/
   - Jinja2: https://jinja.palletsprojects.com/

---

## Quick Reference

### Flask Decorators
```python
@app.route('/path')              # Basic route
@app.route('/path/<int:id>')     # Route with parameter
@app.route('/path', methods=['GET', 'POST'])  # Multiple methods
```

### Database Operations
```python
# Query
all_items = Model.query.all()
one_item = Model.query.get(id)
filtered = Model.query.filter_by(name='John').all()

# Create
new_item = Model(field='value')
db.session.add(new_item)
db.session.commit()

# Update
item.field = 'new value'
db.session.commit()

# Delete
db.session.delete(item)
db.session.commit()
```

### Template Syntax
```html
{{ variable }}                    <!-- Output variable -->
{% if condition %}...{% endif %}  <!-- Conditional -->
{% for item in items %}...{% endfor %}  <!-- Loop -->
{{ url_for('function_name') }}    <!-- Generate URL -->
{% extends "base.html" %}         <!-- Inherit template -->
{% block name %}...{% endblock %} <!-- Define/override block -->
```

---

## Conclusion

You now understand:
- ✅ How Flask applications are structured
- ✅ How routes connect URLs to functions
- ✅ How databases store and retrieve data
- ✅ How templates display dynamic content
- ✅ How forms submit and process data
- ✅ How to add read-only mode for different users

Keep practicing and building! 🚀
