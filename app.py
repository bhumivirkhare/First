from flask import Flask, request, jsonify
import sqlite3
import pandas as pd

app = Flask(__name__)
DB = 'warehouse.db'

# Initialize DB
def init_db():
    with sqlite3.connect(DB) as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS truck_drivers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                license_no TEXT NOT NULL,
                province TEXT NOT NULL,
                age INTEGER NOT NULL
            )
        ''')

# Route to register a new driver
@app.route('/register', methods=['POST'])
def register_driver():
    data = request.get_json()
    with sqlite3.connect(DB) as conn:
        conn.execute('''
            INSERT INTO truck_drivers (name, license_no, province, age)
            VALUES (?, ?, ?, ?)
        ''', (data['name'], data['license_no'], data['province'], data['age']))
    return jsonify({'message': 'Driver registered successfully'}), 201

# Route to view all drivers
@app.route('/drivers', methods=['GET'])
def list_drivers():
    df = pd.read_sql('SELECT * FROM truck_drivers', sqlite3.connect(DB))
    return df.to_json(orient='records')

# Basic analytics: average age, count by province
@app.route('/analytics', methods=['GET'])
def analytics():
    df = pd.read_sql('SELECT * FROM truck_drivers', sqlite3.connect(DB))
    avg_age = df['age'].mean()
    by_province = df['province'].value_counts().to_dict()
    return jsonify({'average_age': avg_age, 'drivers_per_province': by_province})


from flask import render_template

@app.route('/')
def home():
    return render_template('index.html')



if __name__ == '__main__':
    init_db()
    app.run(debug=True)
