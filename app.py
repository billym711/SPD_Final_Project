from flask import Flask, render_template, request, redirect, url_for, flash
from datetime import datetime
import sqlite3

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Helper function to connect to the database
def get_db_connection():
    conn = sqlite3.connect('birthdays.db')  # SQLite database file
    conn.row_factory = sqlite3.Row  # Enables dictionary-like access
    return conn

# Initialize the database using schema.sql
def init_db():
    conn = get_db_connection()
    with open('schema.sql', 'r') as f:
        conn.executescript(f.read())
    conn.close()

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
    user_id = 1  # Replace with dynamic user ID after authentication
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    user_listings = conn.execute('SELECT * FROM listings WHERE user_id = ?', (user_id,)).fetchall()
    user_bookings = conn.execute('SELECT * FROM bookings WHERE user_id = ?', (user_id,)).fetchall()
    user_notifications = conn.execute('SELECT * FROM notifications WHERE user_id = ?', (user_id,)).fetchall()
    conn.close()
    return render_template('dashboard.html', user=user, user_listings=user_listings, user_bookings=user_bookings, user_notifications=user_notifications)

@app.route('/listings', methods=['GET'])
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
    if user is None:
        conn.close()
        flash('User not found.', 'error')
        return redirect(url_for('index'))

    user_listings = conn.execute('SELECT * FROM listings WHERE user_id = ?', (user_id,)).fetchall()
    user_reviews = conn.execute('''
        SELECT reviews.*, users.name AS reviewer_name 
        FROM reviews 
        JOIN users ON reviews.reviewer_id = users.id 
        WHERE reviews.user_id = ?
    ''', (user_id,)).fetchall()
    conn.close()

    return render_template('profile.html', user=user, user_listings=user_listings, user_reviews=user_reviews)


@app.route('/bookings')
def bookings():
    user_id = 1  # Replace with dynamic user ID after authentication
    conn = get_db_connection()
    current_bookings = conn.execute('SELECT * FROM bookings WHERE user_id = ? AND status = "active"', (user_id,)).fetchall()
    past_bookings = conn.execute('SELECT * FROM bookings WHERE user_id = ? AND status = "completed"', (user_id,)).fetchall()
    conn.close()
    return render_template('bookings.html', current_bookings=current_bookings, past_bookings=past_bookings)

@app.route('/book_listing/<int:listing_id>')
def book_listing(listing_id):
    user_id = 1  # Replace with dynamic user ID after authentication
    conn = get_db_connection()
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
        user_id = 1  # Replace with dynamic user ID after authentication
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
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Handle login form submission
        email = request.form['email']
        password = request.form['password']
        
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE email = ? AND password = ?', (email, password)).fetchone()
        conn.close()

        if user:
            flash('Login successful!')
            # Save user information to session here (if using sessions)
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password', 'error')
            return redirect(url_for('login'))
    
    # Render login page
    return render_template('login.html')
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        location = request.form.get('location', '')

        # Directly insert into the database without validation
        conn = get_db_connection()
        conn.execute(
            'INSERT INTO users (name, email, password, location) VALUES (?, ?, ?, ?)',
            (name, email, password, location)
        )
        conn.commit()
        conn.close()

        flash('Registration successful! You can now log in.')
        return redirect(url_for('login'))

    # Render the registration form
    return render_template('register.html')
@app.route('/leave_review/<int:user_id>', methods=['GET', 'POST'])
def leave_review(user_id):
    if request.method == 'POST':
        reviewer_id = 1  # Replace with dynamic user ID from session
        rating = int(request.form['rating'])
        comment = request.form['comment']
        date_posted = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Insert the review into the database
        conn = get_db_connection()
        conn.execute(
            'INSERT INTO reviews (user_id, reviewer_id, rating, comment, date_posted) VALUES (?, ?, ?, ?, ?)',
            (user_id, reviewer_id, rating, comment, date_posted)
        )
        conn.commit()
        conn.close()

        flash('Your review has been submitted successfully!')
        return redirect(url_for('profile', user_id=user_id))

    # Render the review form
    return render_template('leave_review.html', user_id=user_id)



if __name__ == '__main__':
    # Uncomment the following line to initialize the database
    #init_db()
    app.run(debug=True)
