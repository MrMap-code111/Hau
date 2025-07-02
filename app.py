from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'secret_key'

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'database', 'quan_ly_chi_tieu.db')

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == 'Hau' and password == '123678':
            session['user'] = username
            return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM giao_dich ORDER BY ngay DESC')
    giao_dich = cursor.fetchall()
    cursor.execute("SELECT SUM(so_tien) FROM giao_dich WHERE loai = 'thu'")
    tong_thu = cursor.fetchone()[0] or 0
    cursor.execute("SELECT SUM(so_tien) FROM giao_dich WHERE loai = 'chi'")
    tong_chi = cursor.fetchone()[0] or 0
    conn.close()
    return render_template('dashboard.html', giao_dich=giao_dich, tong_thu=tong_thu, tong_chi=tong_chi, current_date=datetime.now().strftime('%Y-%m-%d'))

@app.route('/add', methods=['POST'])
def add_transaction():
    if 'user' not in session:
        return redirect(url_for('login'))
    loai = request.form['loai']
    so_tien = float(request.form['so_tien'])
    danh_muc = request.form['danh_muc']
    mo_ta = request.form['mo_ta']
    ngay = request.form['ngay'] + " 00:00:00"
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('INSERT INTO giao_dich (loai, so_tien, danh_muc, mo_ta, ngay) VALUES (?, ?, ?, ?, ?)', (loai, so_tien, danh_muc, mo_ta, ngay))
    conn.commit()
    conn.close()
    return redirect(url_for('dashboard'))

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))
