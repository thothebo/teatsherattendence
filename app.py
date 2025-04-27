from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from datetime import datetime
import sqlite3

app = Flask(__name__)
app.secret_key = 'مفتاح_سري_للتطبيق'

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # إنشاء جدول المعلمين
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS teachers (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL
        )
    ''')
    
    # إنشاء جدول الحضور مع إضافة حقل الفصل
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY,
            teacher_id INTEGER,
            class_name TEXT,
            classroom_id INTEGER,
            entry_time DATETIME,
            FOREIGN KEY (teacher_id) REFERENCES teachers (id),
            FOREIGN KEY (classroom_id) REFERENCES classrooms (id)
        )
    ''')
    
    # Add classrooms table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS classrooms (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL
        )
    ''')
    
    conn.commit()
    conn.close()

def get_db_connection():
    conn = sqlite3.connect('school_attendance.db')
    conn.row_factory = sqlite3.Row
    return conn

# تهيئة قاعدة البيانات عند بدء التطبيق
init_db()

@app.route('/')
def index():
    conn = get_db_connection()
    teachers = conn.execute('SELECT * FROM teachers').fetchall()
    classrooms = conn.execute('SELECT * FROM classrooms').fetchall()
    attendance = conn.execute('''
        SELECT attendance.id,
               teachers.name as teacher_name, 
               attendance.class_name, 
               classrooms.name as classroom_name, 
               attendance.entry_time
        FROM attendance
        LEFT JOIN teachers ON teachers.id = attendance.teacher_id
        LEFT JOIN classrooms ON classrooms.id = attendance.classroom_id
        ORDER BY attendance.entry_time DESC
    ''').fetchall()
    conn.close()
    return render_template('index.html', teachers=teachers, classrooms=classrooms, attendance=attendance)

@app.route('/manage')
def manage():
    conn = get_db_connection()
    teachers = conn.execute('SELECT * FROM teachers').fetchall()
    classrooms = conn.execute('SELECT * FROM classrooms').fetchall()
    conn.close()
    return render_template('manage.html', teachers=teachers, classrooms=classrooms)

@app.route('/attendance')
def attendance():
    conn = get_db_connection()
    teachers = conn.execute('SELECT * FROM teachers').fetchall()
    classrooms = conn.execute('SELECT * FROM classrooms').fetchall()
    attendance = conn.execute('''
        SELECT attendance.id,
               teachers.name as teacher_name, 
               attendance.class_name, 
               classrooms.name as classroom_name, 
               attendance.entry_time
        FROM attendance
        LEFT JOIN teachers ON teachers.id = attendance.teacher_id
        LEFT JOIN classrooms ON classrooms.id = attendance.classroom_id
        ORDER BY attendance.entry_time DESC
    ''').fetchall()
    conn.close()
    return render_template('attendance.html', teachers=teachers, classrooms=classrooms, attendance=attendance)

@app.route('/add_teacher', methods=['POST'])
def add_teacher():
    name = request.form['name']
    if name:
        conn = get_db_connection()
        conn.execute('INSERT INTO teachers (name) VALUES (?)', (name,))
        conn.commit()
        conn.close()
        flash('تم إضافة المعلم بنجاح')
    return redirect(url_for('manage'))

@app.route('/record_attendance', methods=['POST'])
def record_attendance():
    teacher_id = request.form['teacher_id']
    class_name = request.form['class_name']
    classroom_id = request.form['classroom_id']
    
    if teacher_id and class_name and classroom_id:
        conn = get_db_connection()
        conn.execute('''
            INSERT INTO attendance (teacher_id, class_name, classroom_id, entry_time)
            VALUES (?, ?, ?, ?)
        ''', (teacher_id, class_name, classroom_id, datetime.now()))
        conn.commit()
        conn.close()
        flash('تم تسجيل الحضور بنجاح')
    return redirect(url_for('attendance'))

@app.route('/add_classroom', methods=['POST'])
def add_classroom():
    name = request.form['name']
    if name:
        conn = get_db_connection()
        conn.execute('INSERT INTO classrooms (name) VALUES (?)', (name,))
        conn.commit()
        conn.close()
        flash('تم إضافة الفصل بنجاح')
    return redirect(url_for('manage'))

@app.route('/delete_teacher/<int:id>', methods=['POST'])
def delete_teacher(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM teachers WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    flash('تم حذف المعلم بنجاح')
    return redirect(url_for('manage'))

@app.route('/edit_teacher/<int:id>', methods=['POST'])
def edit_teacher(id):
    name = request.form['name']
    if name:
        conn = get_db_connection()
        conn.execute('UPDATE teachers SET name = ? WHERE id = ?', (name, id))
        conn.commit()
        conn.close()
        flash('تم تعديل اسم المعلم بنجاح')
    return redirect(url_for('manage'))

@app.route('/delete_classroom/<int:id>', methods=['POST'])
def delete_classroom(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM classrooms WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    flash('تم حذف الفصل بنجاح')
    return redirect(url_for('manage'))

@app.route('/edit_classroom/<int:id>', methods=['POST'])
def edit_classroom(id):
    name = request.form['name']
    if name:
        conn = get_db_connection()
        conn.execute('UPDATE classrooms SET name = ? WHERE id = ?', (name, id))
        conn.commit()
        conn.close()
        flash('تم تعديل اسم الفصل بنجاح')
    return redirect(url_for('manage'))

@app.route('/delete_attendance/<int:id>', methods=['POST'])
def delete_attendance(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM attendance WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    flash('تم حذف السجل بنجاح')
    return redirect(url_for('attendance'))

if __name__ == '__main__':
    app.run(debug=True)