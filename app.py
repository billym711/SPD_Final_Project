from flask import Flask, render_template, request, redirect, url_for, flash
from flask import session, redirect, url_for, flash
from datetime import datetime
import sqlite3

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Helper function to connect to the database
def get_db_connection():
    conn = sqlite3.connect('birthdays.db')  # SQLite database file
    conn.row_factory = sqlite3.Row  # Enables dictionary-like access
    return conn

from functools import wraps

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


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

    # Fetch listings without join
    query = 'SELECT * FROM listings WHERE 1=1'
    params = []

    if category:
        query += ' AND category = ?'
        params.append(category)
    if search:
        query += ' AND (title LIKE ? OR description LIKE ?)'
        params.append(f'%{search}%')
        params.append(f'%{search}%')

    listings_data = conn.execute(query, params).fetchall()

    # Fetch owner names separately
    listings = []
    for listing in listings_data:
        owner = conn.execute('SELECT name FROM users WHERE id = ?', (listing['user_id'],)).fetchone()
        listing_with_owner = dict(listing)
        listing_with_owner['owner_name'] = owner['name'] if owner else 'Unknown'
        listings.append(listing_with_owner)

    conn.close()
    return render_template('listings.html', all_listings=listings)


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


@app.route('/bookings', methods=['GET'])
def bookings():
    conn = get_db_connection()
    user_id = 1  # Replace with dynamic user ID from session

    # Fetch current bookings
    current_bookings = conn.execute('''
        SELECT bookings.id AS booking_id, bookings.listing_id AS item_id, 
               bookings.status, listings.title, listings.image_url 
        FROM bookings 
        JOIN listings ON bookings.listing_id = listings.id 
        WHERE bookings.user_id = ? AND bookings.status = 'active'
    ''', (user_id,)).fetchall()

    # Fetch past bookings
    past_bookings = conn.execute('''
        SELECT bookings.id AS booking_id, bookings.listing_id AS item_id, 
               bookings.status, listings.title, listings.image_url 
        FROM bookings 
        JOIN listings ON bookings.listing_id = listings.id 
        WHERE bookings.user_id = ? AND bookings.status = 'completed'
    ''', (user_id,)).fetchall()

    conn.close()
    return render_template(
        'bookings.html',
        current_bookings=current_bookings,
        past_bookings=past_bookings
    )


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
        image_url = request.form.get('image_url', '')
        user_id = 1  # Replace with session or dynamic user ID

        # Insert the new listing into the database
        conn = get_db_connection()
        conn.execute(
            'INSERT INTO listings (user_id, title, description, category, status, date_posted, image_url) VALUES (?, ?, ?, ?, ?, ?, ?)',
            (user_id, title, description, category, 'available', datetime.now(), image_url)
        )
        conn.commit()
        conn.close()

        flash('Listing added successfully!')
        return redirect(url_for('dashboard'))

    return render_template('add_listing.html')


@app.route('/edit_listing/<int:listing_id>', methods=['GET', 'POST'])
def edit_listing(listing_id):
    conn = get_db_connection()
    if request.method == 'POST':
        # Update the listing with the submitted form data
        title = request.form['title']
        description = request.form['description']
        category = request.form['category']
        image_url = request.form['image_url']

        conn.execute(
            'UPDATE listings SET title = ?, description = ?, category = ?, image_url = ? WHERE id = ?',
            (title, description, category, image_url, listing_id)
        )
        conn.commit()
        conn.close()

        flash('Listing updated successfully!')
        return redirect(url_for('dashboard'))

    # Fetch the current listing data for editing
    listing = conn.execute('SELECT * FROM listings WHERE id = ?', (listing_id,)).fetchone()
    conn.close()

    if not listing:
        flash('Listing not found.', 'error')
        return redirect(url_for('dashboard'))

    return render_template('edit_listing.html', listing=listing)

@app.route('/delete_listing/<int:listing_id>', methods=['POST'])
def delete_listing(listing_id):
    conn = get_db_connection()
    listing = conn.execute('SELECT * FROM listings WHERE id = ?', (listing_id,)).fetchone()
    if not listing:
        conn.close()
        flash('Listing not found.', 'error')
        return redirect(url_for('dashboard'))

    conn.execute('DELETE FROM listings WHERE id = ?', (listing_id,))
    conn.commit()
    conn.close()

    flash('Listing deleted successfully!')
    return redirect(url_for('dashboard'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')  # Changed from username to email
        password = request.form.get('password')

        if not email or not password:
            flash('Both email and password are required.', 'error')
            return redirect(url_for('login'))

        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
        conn.close()

        if user and user['password'] == password:  # Replace with hashed password check in production
            session['user_id'] = user['id']
            session['email'] = user['email']
            flash('You are now logged in.', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password.', 'error')

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'success')
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')  # Changed from username to email
        password = request.form.get('password')

        if not email or not password:
            flash('Both email and password are required.', 'error')
            return redirect(url_for('register'))

        conn = get_db_connection()
        conn.execute('INSERT INTO users (email, password) VALUES (?, ?)', (email, password))
        conn.commit()
        conn.close()

        flash('Registration successful. Please log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')



@app.route('/leave_review/<int:user_id>', methods=['GET', 'POST'])
def leave_review(user_id):
    conn = get_db_connection()

    if request.method == 'POST':
        reviewer_id = 1  # Replace with dynamic user ID from session
        rating = int(request.form['rating'])
        comment = request.form['comment']
        date_posted = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Insert the review into the database
        conn.execute(
            'INSERT INTO reviews (user_id, reviewer_id, rating, comment, date_posted) VALUES (?, ?, ?, ?, ?)',
            (user_id, reviewer_id, rating, comment, date_posted)
        )

        # Recalculate reputation score for the reviewed user
        avg_rating = conn.execute(
            'SELECT AVG(rating) AS avg_rating FROM reviews WHERE user_id = ?',
            (user_id,)
        ).fetchone()['avg_rating']

        # Update the user's reputation score
        conn.execute(
            'UPDATE users SET reputation_score = ? WHERE id = ?',
            (int(avg_rating), user_id)
        )

        conn.commit()
        conn.close()

        flash('Your review has been submitted successfully!')
        return redirect(url_for('profile', user_id=user_id))

    # Render the review form
    return render_template('leave_review.html', user_id=user_id)
@app.route('/view_item/<int:item_id>', methods=['GET'])
def view_item(item_id):
    conn = get_db_connection()
    item = conn.execute('SELECT * FROM listings WHERE id = ?', (item_id,)).fetchone()
    conn.close()

    if not item:
        flash('Item not found.', 'error')
        return redirect(url_for('listings'))

    return render_template('view_item.html', item=item)


if __name__ == '__main__':
    # Uncomment the following line to initialize the database
    #init_db()
    app.run(debug=True)
