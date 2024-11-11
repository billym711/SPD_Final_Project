from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)

# Helper function to connect to the database
def get_db_connection():
    conn = sqlite3.connect("birthdays.db")
    conn.row_factory = sqlite3.Row
    return conn

@app.route("/index", methods=["GET", "POST"])
def index():
    conn = get_db_connection()
    if request.method == "POST":
        # Adding a new birthday
        name = request.form.get("name")
        month = request.form.get("month")
        day = request.form.get("day")

        # Insert new birthday into the database
        conn.execute("INSERT INTO birthdays (name, month, day) VALUES (?, ?, ?)", (name, month, day))
        conn.commit()
        conn.close()
        return redirect("/")
    else:
        # Display all birthdays
        birthdays = conn.execute("SELECT id, name, month, day FROM birthdays").fetchall()
        conn.close()
        return render_template("index.html", birthdays=birthdays)

@app.route("/delete/<int:id>", methods=["POST"])
def delete(id):
    conn = get_db_connection()
    conn.execute("DELETE FROM birthdays WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return redirect("/")

@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit(id):
    conn = get_db_connection()
    if request.method == "POST":
        # Update birthday in the database
        name = request.form.get("name")
        month = request.form.get("month")
        day = request.form.get("day")
        conn.execute("UPDATE birthdays SET name = ?, month = ?, day = ? WHERE id = ?", (name, month, day, id))
        conn.commit()
        conn.close()
        return redirect("/")
    else:
        # Fetch the birthday to be edited
        birthday = conn.execute("SELECT id, name, month, day FROM birthdays WHERE id = ?", (id,)).fetchone()
        conn.close()
        return render_template("edit.html", birthday=birthday)

@app.route('/bookings')
def bookings():
    return render_template('bookings.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/listings')
def listings():
    return render_template('listings.html')

@app.route('/profile')
def profile():
    return render_template('profile.html')

if __name__ == "__main__":
    app.run(debug=True)
