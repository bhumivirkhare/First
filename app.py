from flask import Flask, request, jsonify, render_template, send_from_directory
import sqlite3
import pandas as pd
import os

app = Flask(__name__, template_folder='templates')
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

DB = 'warehouse.db'

def init_db():
    with sqlite3.connect(DB) as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS truck_drivers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                license_no TEXT NOT NULL,
                province TEXT NOT NULL,
                age INTEGER NOT NULL,
                document TEXT
            )
        ''')

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/register', methods=['POST'])
def register_driver():
    name = request.form.get('name')
    license_no = request.form.get('license_no')
    province = request.form.get('province')
    age = request.form.get('age')

    file = request.files.get('document')
    filename = None
    if file:
        filename = f"{license_no}_{file.filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

    with sqlite3.connect(DB) as conn:
        conn.execute('''
            INSERT INTO truck_drivers (name, license_no, province, age, document)
            VALUES (?, ?, ?, ?, ?)
        ''', (name, license_no, province, age, filename))

    return jsonify({'message': 'Driver registered successfully'}), 201

@app.route('/drivers', methods=['GET'])
def list_drivers():
    df = pd.read_sql('SELECT * FROM truck_drivers', sqlite3.connect(DB))
    return df.to_json(orient='records')

@app.route('/analytics', methods=['GET'])
def analytics():
    df = pd.read_sql('SELECT * FROM truck_drivers', sqlite3.connect(DB))
    avg_age = df['age'].mean()
    by_province = df['province'].value_counts().to_dict()
    return jsonify({'average_age': avg_age, 'drivers_per_province': by_province})

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
