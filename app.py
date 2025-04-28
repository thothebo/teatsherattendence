import os
from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your_secret_key_here')

# تحديد مسار قاعدة البيانات
DATABASE_PATH = '/tmp/school_attendance.db'

def init_db():
    """تهيئة قاعدة البيانات وإنشاء الجداول الأساسية"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        # إنشاء جدول المعلمين
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS teachers (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL
            )
        ''')
        
        # إنشاء جدول الفصول
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS classrooms (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL
            )
        ''')
        
        # إنشاء جدول الحضور
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
        conn.commit()
    except sqlite3.Error as e:
        print(f"خطأ في تهيئة قاعدة البيانات: {e}")
        raise
    finally:
        conn.close()

def get_db():
    """إنشاء اتصال بقاعدة البيانات"""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# تهيئة قاعدة البيانات عند بدء التطبيق
with app.app_context():
    if not os.path.exists(DATABASE_PATH):
        init_db()

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

@app.route('/edit_teacher/<int:id>', methods=['POST'])
def edit_teacher(id):
    name = request.form['name']
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE teachers SET name = ? WHERE id = ?", (name, id))
    conn.commit()
    conn.close()
    flash('تم تعديل المعلم بنجاح')
    return redirect(url_for('manage'))

@app.route('/edit_classroom/<int:id>', methods=['POST'])
def edit_classroom(id):
    name = request.form['name']
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE classrooms SET name = ? WHERE id = ?", (name, id))
    conn.commit()
    conn.close()
    flash('تم تعديل الفصل بنجاح')
    return redirect(url_for('manage'))

@app.route('/delete_classroom/<int:id>', methods=['POST'])
def delete_classroom(id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM classrooms WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    flash('تم حذف الفصل بنجاح')
    return redirect(url_for('manage'))

@app.route('/delete_teacher/<int:id>', methods=['POST'])
def delete_teacher(id):
    conn = get_db()
    cursor = conn.cursor()
    try:
        # First delete related attendance records
        cursor.execute("DELETE FROM attendance WHERE teacher_id = ?", (id,))
        # Then delete the teacher
        cursor.execute("DELETE FROM teachers WHERE id = ?", (id,))
        conn.commit()
        flash('تم حذف المعلم بنجاح')
    except sqlite3.Error as e:
        conn.rollback()
        flash('حدث خطأ أثناء حذف المعلم')
    finally:
        conn.close()
    return redirect(url_for('manage'))

# التأكد من وجود المجلد وإمكانية الكتابة فيه
if not os.path.exists('/tmp'):
    os.makedirs('/tmp', exist_ok=True)

if __name__ == '__main__':
    app.run(debug=True)
