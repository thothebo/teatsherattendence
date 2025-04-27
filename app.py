from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Required for flash messages

def get_db():
    conn = sqlite3.connect('school_attendance.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT teachers.name as teacher_name, attendance.class_name, 
               classrooms.name as classroom_name, attendance.entry_time, attendance.id
        FROM attendance
        JOIN teachers ON teachers.id = attendance.teacher_id
        JOIN classrooms ON classrooms.id = attendance.classroom_id
        ORDER BY attendance.entry_time DESC
    """)
    attendance = cursor.fetchall()
    conn.close()
    return render_template('index.html', attendance=attendance)

@app.route('/manage')
def manage():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM teachers")
    teachers = cursor.fetchall()
    cursor.execute("SELECT id, name FROM classrooms")
    classrooms = cursor.fetchall()
    conn.close()
    return render_template('manage.html', teachers=teachers, classrooms=classrooms)

@app.route('/attendance')
def attendance():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM teachers")
    teachers = cursor.fetchall()
    cursor.execute("SELECT id, name FROM classrooms")
    classrooms = cursor.fetchall()
    cursor.execute("""
        SELECT teachers.name as teacher_name, attendance.class_name, 
               classrooms.name as classroom_name, attendance.entry_time, attendance.id
        FROM attendance
        JOIN teachers ON teachers.id = attendance.teacher_id
        JOIN classrooms ON classrooms.id = attendance.classroom_id
        ORDER BY attendance.entry_time DESC
    """)
    attendance = cursor.fetchall()
    conn.close()
    return render_template('attendance.html', teachers=teachers, classrooms=classrooms, attendance=attendance)

@app.route('/add_teacher', methods=['POST'])
def add_teacher():
    name = request.form['name']
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO teachers (name) VALUES (?)", (name,))
    conn.commit()
    conn.close()
    flash('تم إضافة المعلم بنجاح')
    return redirect(url_for('manage'))

@app.route('/add_classroom', methods=['POST'])
def add_classroom():
    name = request.form['name']
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO classrooms (name) VALUES (?)", (name,))
    conn.commit()
    conn.close()
    flash('تم إضافة الفصل بنجاح')
    return redirect(url_for('manage'))

@app.route('/record_attendance', methods=['POST'])
def record_attendance():
    teacher_id = request.form['teacher_id']
    class_name = request.form['class_name']
    classroom_id = request.form['classroom_id']
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO attendance (teacher_id, class_name, classroom_id, entry_time)
        VALUES (?, ?, ?, ?)
    """, (teacher_id, class_name, classroom_id, datetime.now()))
    conn.commit()
    conn.close()
    flash('تم تسجيل الحضور بنجاح')
    return redirect(url_for('attendance'))

@app.route('/delete_attendance/<int:id>', methods=['POST'])
def delete_attendance(id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM attendance WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    flash('تم حذف السجل بنجاح')
    return redirect(url_for('attendance'))

if __name__ == '__main__':
    app.run(debug=True)
