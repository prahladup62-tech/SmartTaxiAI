import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash

import config

app = Flask(__name__)
app.config['SECRET_KEY'] = config.SECRET_KEY
DATABASE_PATH = os.path.join(os.path.dirname(__file__), 'database.db')
SCHEMA_FILE = os.path.join(os.path.dirname(__file__), 'database.sql')


def get_db():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def seed_data(conn):
    cars = [
        ('Toyota Innova Crysta', 7, '₹3,200 / day', 'Spacious SUV for family trips with luggage space.', 'https://images.unsplash.com/photo-1511919884226-fd3cad34687c?auto=format&fit=crop&w=800&q=80'),
        ('Honda City', 4, '₹2,100 / day', 'Comfortable sedan for city travel and outstation rides.', 'https://images.unsplash.com/photo-1525609004556-c46c7d6cf023?auto=format&fit=crop&w=800&q=80'),
        ('Mercedes-Benz V-Class', 7, '₹5,500 / day', 'Premium business travel with leather seats and AC.', 'https://images.unsplash.com/photo-1493238792000-8113da705763?auto=format&fit=crop&w=800&q=80')
    ]
    reviews = [
        ('Rahul', 5, 'Excellent service, clean car and on-time pick up.'),
        ('Pooja', 5, 'Very responsive team and safe drive. Highly recommended!'),
        ('Manish', 4, 'Good vehicle and friendly driver. Booked again for my next trip.')
    ]

    conn.executemany(
        'INSERT INTO cars (make_model, seats, price_per_day, description, image_url) VALUES (?, ?, ?, ?, ?)',
        cars
    )
    conn.executemany(
        'INSERT INTO reviews (user_name, rating, comment) VALUES (?, ?, ?)',
        reviews
    )


def init_db():
    database_exists = os.path.exists(DATABASE_PATH)
    conn = get_db()

    with open(SCHEMA_FILE, 'r', encoding='utf-8') as f:
        conn.executescript(f.read())

    if not database_exists:
        seed_data(conn)

    conn.commit()
    conn.close()


with app.app_context():
    init_db()


def get_current_user():
    return session.get('user')


@app.route('/')
def index():
    conn = get_db()
    cars = conn.execute('SELECT * FROM cars WHERE available = 1').fetchall()
    reviews = conn.execute('SELECT * FROM reviews ORDER BY created_at DESC LIMIT 3').fetchall()
    conn.close()
    return render_template('index.html', user=get_current_user(), cars=cars, reviews=reviews)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '').strip()

        if not name or not email or not password:
            flash('All fields are required.', 'warning')
            return redirect(url_for('register'))

        password_hash = generate_password_hash(password)
        conn = get_db()
        try:
            conn.execute(
                'INSERT INTO users (name, email, password) VALUES (?, ?, ?)',
                (name, email, password_hash)
            )
            conn.commit()
            flash('Registration successful. Please log in.', 'success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('This email is already registered.', 'danger')
        finally:
            conn.close()

    return render_template('register.html', user=get_current_user())


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '').strip()

        conn = get_db()
        user = conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
        conn.close()

        if user and check_password_hash(user['password'], password):
            session['user'] = {'id': user['id'], 'name': user['name'], 'email': user['email']}
            flash('Logged in successfully.', 'success')
            return redirect(url_for('dashboard'))

        flash('Invalid email or password.', 'danger')
        return redirect(url_for('login'))

    return render_template('login.html', user=get_current_user())


@app.route('/logout')
def logout():
    session.pop('user', None)
    session.pop('admin', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))


@app.route('/dashboard')
def dashboard():
    user = get_current_user()
    if not user:
        flash('Please log in to view your dashboard.', 'warning')
        return redirect(url_for('login'))

    conn = get_db()
    bookings = conn.execute('SELECT * FROM bookings WHERE user_id = ? ORDER BY created_at DESC', (user['id'],)).fetchall()
    conn.close()

    return render_template('dashboard.html', user=user, bookings=bookings)


@app.route('/booking', methods=['GET', 'POST'])
def booking():
    user = get_current_user()
    if not user:
        flash('You must log in to make a booking.', 'warning')
        return redirect(url_for('login'))

    if request.method == 'POST':
        trip_type = request.form.get('trip_type', '').strip()
        pickup = request.form.get('pickup', '').strip()
        dropoff = request.form.get('dropoff', '').strip()
        travel_date = request.form.get('travel_date', '').strip()

        if not trip_type or not pickup or not dropoff or not travel_date:
            flash('Please complete all booking fields.', 'warning')
            return redirect(url_for('booking'))

        conn = get_db()
        conn.execute(
            'INSERT INTO bookings (user_id, trip_type, pickup, dropoff, travel_date) VALUES (?, ?, ?, ?, ?)',
            (user['id'], trip_type, pickup, dropoff, travel_date)
        )
        conn.commit()
        conn.close()

        flash('Your booking request has been submitted. Our team will contact you shortly.', 'success')
        return redirect(url_for('dashboard'))

    return render_template('booking.html', user=user)


@app.route('/profile', methods=['GET', 'POST'])
def profile():
    user = get_current_user()
    if not user:
        flash('Please log in to access your profile.', 'warning')
        return redirect(url_for('login'))

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        if not name:
            flash('Name cannot be empty.', 'warning')
            return redirect(url_for('profile'))

        conn = get_db()
        conn.execute('UPDATE users SET name = ? WHERE id = ?', (name, user['id']))
        conn.commit()
        conn.close()

        session['user']['name'] = name
        flash('Profile updated successfully.', 'success')
        return redirect(url_for('profile'))

    return render_template('profile.html', user=user)


@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if session.get('admin'):
        return redirect(url_for('admin_dashboard'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()

        if username == config.ADMIN_USERNAME and password == config.ADMIN_PASSWORD:
            session['admin'] = {'username': username}
            flash('Admin access granted.', 'success')
            return redirect(url_for('admin_dashboard'))

        flash('Invalid admin credentials.', 'danger')
        return redirect(url_for('admin_login'))

    return render_template('admin/login.html', user=None)


@app.route('/admin/logout')
def admin_logout():
    session.pop('admin', None)
    flash('Admin logged out.', 'info')
    return redirect(url_for('index'))


def admin_required(view):
    def wrapped(*args, **kwargs):
        if not session.get('admin'):
            flash('Admin sign-in required.', 'warning')
            return redirect(url_for('admin_login'))
        return view(*args, **kwargs)

    wrapped.__name__ = view.__name__
    return wrapped


@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    conn = get_db()
    stats = {
        'users': conn.execute('SELECT COUNT(*) FROM users').fetchone()[0],
        'bookings': conn.execute('SELECT COUNT(*) FROM bookings').fetchone()[0],
        'cars': conn.execute('SELECT COUNT(*) FROM cars').fetchone()[0],
        'reviews': conn.execute('SELECT COUNT(*) FROM reviews').fetchone()[0]
    }
    conn.close()
    return render_template('admin/dashboard.html', user=None, stats=stats)


@app.route('/admin/bookings')
@admin_required
def admin_bookings():
    conn = get_db()
    bookings = conn.execute(
        'SELECT b.id, b.trip_type, b.pickup, b.dropoff, b.travel_date, b.created_at, u.name AS user_name, u.email AS user_email '
        'FROM bookings b JOIN users u ON b.user_id = u.id ORDER BY b.created_at DESC'
    ).fetchall()
    conn.close()
    return render_template('admin/bookings.html', user=None, bookings=bookings)


@app.route('/admin/users')
@admin_required
def admin_users():
    conn = get_db()
    users = conn.execute('SELECT id, name, email, created_at FROM users ORDER BY created_at DESC').fetchall()
    conn.close()
    return render_template('admin/users.html', user=None, users=users)


@app.route('/admin/cars')
@admin_required
def admin_cars():
    conn = get_db()
    cars = conn.execute('SELECT * FROM cars ORDER BY id').fetchall()
    conn.close()
    return render_template('admin/cars.html', user=None, cars=cars)


@app.route('/admin/reviews')
@admin_required
def admin_reviews():
    conn = get_db()
    reviews = conn.execute('SELECT * FROM reviews ORDER BY created_at DESC').fetchall()
    conn.close()
    return render_template('admin/reviews.html', user=None, reviews=reviews)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
