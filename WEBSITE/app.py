from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "super_secret_key"

DATABASE = "users.db"

def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS locations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            medicines TEXT NOT NULL,
            latitude TEXT NOT NULL,
            longitude TEXT NOT NULL,
            time TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def home():
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

        try:
            conn = sqlite3.connect(DATABASE)
            cursor = conn.cursor()
            cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
            conn.commit()
            conn.close()
            flash('Registration successful! You can now login.', 'success')
            return redirect(url_for('home'))
        except sqlite3.IntegrityError:
            flash('Username already exists!', 'danger')
            return redirect(url_for('register'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        conn.close()

        if user and check_password_hash(user[2], password):
            session['user_id'] = user[0]
            session['username'] = user[1]
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid credentials!', 'danger')
            return redirect(url_for('home'))
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        flash('Please log in to view this page.', 'danger')
        return redirect(url_for('home'))
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM locations")
    locations = cursor.fetchall()
    conn.close()

    return render_template('dashboard.html', locations=locations)

@app.route('/get_locations', methods=['POST'])
def get_locations():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT name, medicines, latitude, longitude, time FROM locations")
    locations = cursor.fetchall()
    conn.close()

    # Convert the locations into a list of dictionaries for JSON response
    locations_list = []
    for location in locations:
        locations_list.append({
            'name': location[0],
            'medicines': location[1],
            'latitude': location[2],
            'longitude': location[3],
            'time': location[4]
        })

    return {"locations": locations_list}


@app.route('/post_location', methods=['POST'])
def post_location():
    if request.method == 'POST':
        data = request.get_json()  # Get JSON data from the request
        name = data.get('name')
        medicines = data.get('medicines')
        latitude = data.get('latitude')
        longitude = data.get('longitude')
        time = data.get('time')

        if not all([name, medicines, latitude, longitude, time]):
            return "Invalid data!", 400

        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()

        # Check if location exists
        cursor.execute("SELECT id FROM locations WHERE name = ?", (name,))
        existing_location = cursor.fetchone()

        if existing_location:
            # Update record
            cursor.execute("""
                UPDATE locations 
                SET medicines = ?, latitude = ?, longitude = ?, time = ? 
                WHERE name = ?
            """, (medicines, latitude, longitude, time, name))
        else:
            # Insert new record
            cursor.execute("""
                INSERT INTO locations (name, medicines, latitude, longitude, time) 
                VALUES (?, ?, ?, ?, ?)
            """, (name, medicines, latitude, longitude, time))

        conn.commit()
        conn.close()
        return {"message": "Location updated!"}, 200


@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully!', 'success')
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5050)
