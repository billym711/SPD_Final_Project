from flask import Flask, render_template, request, redirect, url_for, flash
from datetime import datetime
import sqlite3

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Database helper functions
def get_db_connection():
    conn = sqlite3.connect('birthdays.db')  # Update with your database name
    conn.row_factory = sqlite3.Row
    return conn

# Routes
@app.route('/')
def index():
    conn = get_db_connection()
    recent_listings = conn.execute('SELECT * FROM listings ORDER BY date_posted DESC LIMIT 5').fetchall()
    top_rated_users = conn.execute('SELECT * FROM users ORDER BY reputation_score DESC LIMIT 5').fetchall()
    conn.close()
    return render_template('index.html', recent_listings=recent_listings, top_rated_users=top_rated_users)

@app.route('/dashboard')
def dashboard():
    conn = get_db_connection()
    user_id = 1  # Replace with dynamic user ID after implementing authentication
    user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    user_listings = conn.execute('SELECT * FROM listings WHERE user_id = ?', (user_id,)).fetchall()
    user_bookings = conn.execute('SELECT * FROM bookings WHERE user_id = ?', (user_id,)).fetchall()
    user_notifications = conn.execute('SELECT * FROM notifications WHERE user_id = ?', (user_id,)).fetchall()
    conn.close()
    return render_template('dashboard.html', user=user, user_listings=user_listings, user_bookings=user_bookings, user_notifications=user_notifications)

@app.route('/listings', methods=['GET', 'POST'])
def listings():
    conn = get_db_connection()
    category = request.args.get('category', '')
    search = request.args.get('search', '')

    query = 'SELECT * FROM listings WHERE 1=1'
    params = []

    if category:
        query += ' AND category = ?'
        params.append(category)
    if search:
        query += ' AND (title LIKE ? OR description LIKE ?)'
        params.append(f'%{search}%')
        params.append(f'%{search}%')

    all_listings = conn.execute(query, params).fetchall()
    conn.close()
    return render_template('listings.html', all_listings=all_listings)

@app.route('/profile/<int:user_id>')
def profile(user_id):
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    user_listings = conn.execute('SELECT * FROM listings WHERE user_id = ?', (user_id,)).fetchall()
    user_reviews = conn.execute('SELECT * FROM reviews WHERE user_id = ?', (user_id,)).fetchall()
    conn.close()
    return render_template('profile.html', user=user, user_listings=user_listings, user_reviews=user_reviews)

@app.route('/bookings')
def bookings():
    conn = get_db_connection()
    user_id = 1  # Replace with dynamic user ID after implementing authentication
    current_bookings = conn.execute('SELECT * FROM bookings WHERE user_id = ? AND status = "active"', (user_id,)).fetchall()
    past_bookings = conn.execute('SELECT * FROM bookings WHERE user_id = ? AND status = "completed"', (user_id,)).fetchall()
    conn.close()
    return render_template('bookings.html', current_bookings=current_bookings, past_bookings=past_bookings)

@app.route('/book_listing/<int:listing_id>')
def book_listing(listing_id):
    conn = get_db_connection()
    user_id = 1  # Replace with dynamic user ID after implementing authentication
    conn.execute('INSERT INTO bookings (user_id, listing_id, status, booking_date) VALUES (?, ?, ?, ?)', 
                 (user_id, listing_id, 'active', datetime.now()))
    conn.commit()
    conn.close()
    flash('Booking successful!')
    return redirect(url_for('bookings'))

@app.route('/cancel_booking/<int:booking_id>')
def cancel_booking(booking_id):
    conn = get_db_connection()
    conn.execute('UPDATE bookings SET status = "cancelled" WHERE id = ?', (booking_id,))
    conn.commit()
    conn.close()
    flash('Booking cancelled!')
    return redirect(url_for('bookings'))

@app.route('/add_listing', methods=['GET', 'POST'])
def add_listing():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        category = request.form['category']
        user_id = 1  # Replace with dynamic user ID after implementing authentication
        conn = get_db_connection()
        conn.execute('INSERT INTO listings (user_id, title, description, category, status, date_posted) VALUES (?, ?, ?, ?, ?, ?)', 
                     (user_id, title, description, category, 'available', datetime.now()))
        conn.commit()
        conn.close()
        flash('Listing added successfully!')
        return redirect(url_for('dashboard'))
    return render_template('add_listing.html')

@app.route('/edit_listing/<int:listing_id>', methods=['GET', 'POST'])
def edit_listing(listing_id):
    conn = get_db_connection()
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        category = request.form['category']
        conn.execute('UPDATE listings SET title = ?, description = ?, category = ? WHERE id = ?', 
                     (title, description, category, listing_id))
        conn.commit()
        conn.close()
        flash('Listing updated successfully!')
        return redirect(url_for('dashboard'))
    listing = conn.execute('SELECT * FROM listings WHERE id = ?', (listing_id,)).fetchone()
    conn.close()
    return render_template('edit_listing.html', listing=listing)

if __name__ == '__main__':
    app.run(debug=True)
