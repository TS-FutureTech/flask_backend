from flask import Flask, render_template, request, redirect, url_for, jsonify
import sqlite3
from datetime import datetime

app = Flask(__name__)

# Initialize the database
def initialize_database():
    conn = sqlite3.connect('finance.db')
    c = conn.cursor()
    
    c.execute('''CREATE TABLE IF NOT EXISTS donations
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, amount REAL, purpose TEXT, date TEXT)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS expenditures
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, description TEXT, amount REAL, category TEXT, date TEXT)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS assets
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, amount REAL, condition TEXT, date TEXT)''')
    
    conn.commit()
    conn.close()

# Add a record to the database
def add_record(record_type, data):
    conn = sqlite3.connect('finance.db')
    c = conn.cursor()
    
    data['date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    if record_type == 'donations':
        c.execute('''INSERT INTO donations (name, amount, purpose, date)
                     VALUES (?, ?, ?, ?)''', (data['name'], data['amount'], data['purpose'], data['date']))
    elif record_type == 'expenditures':
        c.execute('''INSERT INTO expenditures (description, amount, category, date)
                     VALUES (?, ?, ?, ?)''', (data['description'], data['amount'], data['category'], data['date']))
    elif record_type == 'assets':
        c.execute('''INSERT INTO assets (name, amount, condition, date)
                     VALUES (?, ?, ?, ?)''', (data['name'], data['amount'], data['condition'], data['date']))
    
    conn.commit()
    conn.close()

# View records from the database
def view_records(table):
    conn = sqlite3.connect('finance.db')
    c = conn.cursor()
    
    c.execute(f'SELECT * FROM {table}')
    records = c.fetchall()
    
    conn.close()
    return records

# Generate financial summary
def financial_summary():
    conn = sqlite3.connect('finance.db')
    c = conn.cursor()
    
    c.execute('SELECT SUM(amount) FROM donations')
    total_donations = c.fetchone()[0] or 0
    
    c.execute('SELECT SUM(amount) FROM expenditures')
    total_expenditures = c.fetchone()[0] or 0
    
    balance = total_donations - total_expenditures
    
    c.execute('SELECT SUM(amount) FROM assets')
    total_assets = c.fetchone()[0] or 0
    
    conn.close()
    return total_donations, total_expenditures, balance, total_assets

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/add', methods=['POST'])
def add():
    data = request.json
    record_type = data['record_type']
    add_record(record_type, data)
    return jsonify({"status": "success"})

@app.route('/view/<table>')
def view(table):
    if table in ['donations', 'expenditures', 'assets']:
        records = view_records(table)
        return jsonify(records)
    return jsonify({"error": "Invalid table"})

@app.route('/summary')
def summary():
    total_donations, total_expenditures, balance, total_assets = financial_summary()
    return jsonify({
        "total_donations": total_donations,
        "total_expenditures": total_expenditures,
        "balance": balance,
        "total_assets": total_assets
    })

if __name__ == '__main__':
    initialize_database()
    app.run(debug=True, host='0.0.0.0', port=5000)