from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
import hashlib
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'secret_key_123'

# Đường dẫn tuyệt đối tới file SQLite
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'database', 'quan_ly_chi_tieu.db')

# Mã hóa mật khẩu như phần mềm gốc
def ma_hoa_mat_khau(mat_khau):
    return hashlib.md5(mat_khau.encode('utf-8')).hexdigest()

# Kiểm tra đăng nhập
def kiem_tra_dang_nhap(ten_dang_nhap, mat_khau):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT mat_khau FROM tai_khoan WHERE ten_dang_nhap = ?', (ten_dang_nhap,))
    row = cursor.fetchone()
    conn.close()
    if row and row[0] == ma_hoa_mat_khau(mat_khau):
        return True
    return False

# Trang đăng nhập
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        ten_dang_nhap = request.form['username']
        mat_khau = request.form['password']
        if kiem_tra_dang_nhap(ten_dang_nhap, mat_khau):
            session['user'] = ten_dang_nhap
            return redirect(url_for('dashboard'))
        else:
            flash("Sai tên đăng nhập hoặc mật khẩu!", "danger")
    return render_template('login.html')

# Trang dashboard (hiển thị danh sách giao dịch)
@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Lấy danh sách giao dịch
    cursor.execute('SELECT * FROM giao_dich ORDER BY ngay DESC')
    giao_dich = cursor.fetchall()

    # Tính tổng thu và tổng chi
    cursor.execute("SELECT SUM(so_tien) FROM giao_dich WHERE loai = 'thu'")
    tong_thu = cursor.fetchone()[0] or 0

    cursor.execute("SELECT SUM(so_tien) FROM giao_dich WHERE loai = 'chi'")
    tong_chi = cursor.fetchone()[0] or 0

    conn.close()

    return render_template(
        'dashboard.html',
        giao_dich=giao_dich,
        tong_thu=tong_thu,
        tong_chi=tong_chi,
        current_date=datetime.now().strftime('%Y-%m-%d')
    )


# Route thêm giao dịch mới
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
    cursor.execute('''
        INSERT INTO giao_dich (loai, so_tien, danh_muc, mo_ta, ngay)
        VALUES (?, ?, ?, ?, ?)
    ''', (loai, so_tien, danh_muc, mo_ta, ngay))
    conn.commit()
    conn.close()

    return redirect(url_for('dashboard'))
@app.route('/delete/<int:id>', methods=['POST'])
def delete_transaction(id):
    if 'user' not in session:
        return redirect(url_for('login'))

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM giao_dich WHERE id = ?', (id,))
    conn.commit()
    conn.close()

    return redirect(url_for('dashboard'))

# Đăng xuất
@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

# Khởi động ứng dụng
if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 10000))  # 10000 là dự phòng khi chạy local
    app.run(host='0.0.0.0', port=port)

