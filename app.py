from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date
from functools import wraps
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'fallback-key-12345')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///reservations.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'Jezera2017')

db = SQLAlchemy(app)

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

    def __repr__(self):
        return f'<Reservation {self.guest_name} - {self.check_in}>'

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

def require_admin(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_logged_in'):
            flash('Please login as admin to access this page', 'error')
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

def check_readonly(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('readonly_mode'):
            flash('You are in read-only mode. You cannot modify reservations.', 'error')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    if session.get('admin_logged_in'):
        return redirect(url_for('index'))
    if request.method == 'POST':
        password = request.form.get('password')
        if password == ADMIN_PASSWORD:
            session['admin_logged_in'] = True
            session.pop('readonly_mode', None)
            flash('Logged in as Admin', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid admin password', 'error')
    return render_template('admin_login.html')

@app.route('/admin-logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    flash('Logged out from admin mode', 'success')
    return redirect(url_for('admin_login'))

@app.route('/readonly')
def readonly_access():
    session['readonly_mode'] = True
    session.pop('admin_logged_in', None)
    flash('Viewing in read-only mode', 'success')
    return redirect(url_for('index'))

@app.route('/exit-readonly')
def exit_readonly():
    session.pop('readonly_mode', None)
    flash('Exited read-only mode', 'success')
    return redirect(url_for('login_select'))

@app.route('/')
def index():
    if not session.get('admin_logged_in') and not session.get('readonly_mode'):
        return redirect(url_for('login_select'))
    reservations = Reservation.query.order_by(Reservation.check_in).all()
    is_readonly = session.get('readonly_mode', False)
    is_admin = session.get('admin_logged_in', False)
    today = date.today()
    return render_template('index.html', reservations=reservations, is_readonly=is_readonly, is_admin=is_admin, today=today)

@app.route('/login-select')
def login_select():
    if session.get('admin_logged_in') or session.get('readonly_mode'):
        return redirect(url_for('index'))
    return render_template('login_select.html')

@app.route('/add', methods=['GET', 'POST'])
@require_admin
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

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
@require_admin
@check_readonly
def edit_reservation(id):
    reservation = Reservation.query.get_or_404(id)
    if request.method == 'POST':
        try:
            reservation.guest_name = request.form['guest_name']
            reservation.platform = request.form['platform']
            reservation.check_in = datetime.strptime(request.form['check_in'], '%Y-%m-%d').date()
            reservation.check_out = datetime.strptime(request.form['check_out'], '%Y-%m-%d').date()
            reservation.adults = int(request.form['adults'])
            reservation.children = int(request.form['children'])
            reservation.special_requests = request.form.get('special_requests', '')
            reservation.notes = request.form.get('notes', '')
            if reservation.check_out <= reservation.check_in:
                flash('Check-out date must be after check-in date!', 'error')
                return redirect(url_for('edit_reservation', id=id))
            db.session.commit()
            flash('Reservation updated successfully!', 'success')
            return redirect(url_for('index'))
        except Exception as e:
            flash(f'Error updating reservation: {str(e)}', 'error')
            return redirect(url_for('edit_reservation', id=id))
    return render_template('edit_reservation.html', reservation=reservation)

@app.route('/delete/<int:id>')
@require_admin
@check_readonly
def delete_reservation(id):
    reservation = Reservation.query.get_or_404(id)
    try:
        db.session.delete(reservation)
        db.session.commit()
        flash('Reservation deleted successfully!', 'success')
    except Exception as e:
        flash(f'Error deleting reservation: {str(e)}', 'error')
    return redirect(url_for('index'))

@app.route('/api/reservations')
def api_reservations():
    reservations = Reservation.query.all()
    return jsonify([r.to_dict() for r in reservations])

@app.route('/calendar')
def calendar_view():
    if not session.get('admin_logged_in') and not session.get('readonly_mode'):
        return redirect(url_for('login_select'))
    reservations = Reservation.query.order_by(Reservation.check_in).all()
    is_readonly = session.get('readonly_mode', False)
    is_admin = session.get('admin_logged_in', False)
    today = date.today()
    return render_template('calendar.html', reservations=reservations, is_readonly=is_readonly, is_admin=is_admin, today=today)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)