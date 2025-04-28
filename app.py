import os
from flask import Flask, render_template, request, redirect, url_for, flash, g
import sqlite3
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your_secret_key_here')

# تعريف واحد لمسار قاعدة البيانات
DATABASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'database.db')

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
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS supervision (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                teacher_id INTEGER NOT NULL,
                date DATE NOT NULL,
                shift_type TEXT NOT NULL,
                notes TEXT,
                FOREIGN KEY (teacher_id) REFERENCES teachers (id)
            )
        """)
        conn.commit()
    except sqlite3.Error as e:
        print(f"خطأ في تهيئة قاعدة البيانات: {e}")
        raise
    finally:
        conn.close()

def get_db():
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = sqlite3.connect(DATABASE)
        g.sqlite_db.row_factory = sqlite3.Row
    return g.sqlite_db

@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()

# تهيئة قاعدة البيانات عند بدء التطبيق
db_dir = os.path.dirname(DATABASE)
if not os.path.exists(db_dir):
    os.makedirs(db_dir, exist_ok=True)

with app.app_context():
    if not os.path.exists(DATABASE):
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

@app.route('/supervision')
def supervision():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM teachers")
    teachers = cursor.fetchall()
    cursor.execute("""
        SELECT supervision.id, teachers.name as teacher_name, 
               supervision.date, supervision.shift_type, supervision.notes
        FROM supervision
        JOIN teachers ON teachers.id = supervision.teacher_id
        ORDER BY supervision.date DESC
    """)
    supervisions = cursor.fetchall()
    conn.close()
    return render_template('supervision.html', teachers=teachers, supervisions=supervisions)

@app.route('/add_supervision', methods=['POST'])
def add_supervision():
    teacher_id = request.form['teacher_id']
    shift_type = request.form['shift_type']
    notes = request.form['notes']
    date = datetime.now().date()
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO supervision (teacher_id, date, shift_type, notes)
        VALUES (?, ?, ?, ?)
    """, (teacher_id, date, shift_type, notes))
    conn.commit()
    conn.close()
    flash('تم تسجيل المناوبة بنجاح')
    return redirect(url_for('supervision'))

@app.route('/delete_supervision/<int:id>', methods=['POST'])
def delete_supervision(id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM supervision WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    flash('تم حذف سجل المناوبة بنجاح')
    return redirect(url_for('supervision'))

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

@app.route('/daily_report')
def daily_report():
    conn = get_db()
    cursor = conn.cursor()
    today = datetime.now().date()
    
    # تقرير الحضور اليومي
    cursor.execute("""
        SELECT teachers.name as teacher_name, attendance.class_name, 
               classrooms.name as classroom_name, attendance.entry_time
        FROM attendance
        JOIN teachers ON teachers.id = attendance.teacher_id
        JOIN classrooms ON classrooms.id = attendance.classroom_id
        WHERE DATE(attendance.entry_time) = ?
        ORDER BY attendance.entry_time DESC
    """, (today,))
    daily_attendance = cursor.fetchall()
    
    # تقرير المناوبة اليومي
    cursor.execute("""
        SELECT teachers.name as teacher_name, supervision.shift_type, 
               supervision.notes
        FROM supervision
        JOIN teachers ON teachers.id = supervision.teacher_id
        WHERE DATE(supervision.date) = ?
        ORDER BY supervision.shift_type
    """, (today,))
    daily_supervision = cursor.fetchall()
    
    conn.close()
    return render_template('daily_report.html', 
                         attendance=daily_attendance, 
                         supervision=daily_supervision,
                         date=today)

@app.route('/weekly_report')
def weekly_report():
    conn = get_db()
    cursor = conn.cursor()
    
    # حساب تاريخ بداية ونهاية الأسبوع
    today = datetime.now().date()
    start_of_week = today - timedelta(days=today.weekday())
    end_of_week = start_of_week + timedelta(days=6)
    
    # تقرير الحضور الأسبوعي
    cursor.execute("""
        SELECT 
            teachers.name as teacher_name,
            COUNT(*) as attendance_count,
            GROUP_CONCAT(DISTINCT classrooms.name) as classrooms
        FROM attendance
        JOIN teachers ON teachers.id = attendance.teacher_id
        JOIN classrooms ON classrooms.id = attendance.classroom_id
        WHERE DATE(attendance.entry_time) BETWEEN ? AND ?
        GROUP BY teachers.id, teachers.name
        ORDER BY attendance_count DESC
    """, (start_of_week, end_of_week))
    weekly_attendance = cursor.fetchall()
    
    # تقرير المناوبة الأسبوعي
    cursor.execute("""
        SELECT 
            teachers.name as teacher_name,
            COUNT(*) as supervision_count,
            GROUP_CONCAT(DISTINCT supervision.shift_type) as shift_types
        FROM supervision
        JOIN teachers ON teachers.id = supervision.teacher_id
        WHERE DATE(supervision.date) BETWEEN ? AND ?
        GROUP BY teachers.id, teachers.name
        ORDER BY supervision_count DESC
    """, (start_of_week, end_of_week))
    weekly_supervision = cursor.fetchall()
    
    conn.close()
    return render_template('weekly_report.html',
                         attendance=weekly_attendance,
                         supervision=weekly_supervision,
                         start_date=start_of_week,
                         end_date=end_of_week)

if __name__ == '__main__':
    app.run(debug=True)

# حذف الكود القديم الخاص بمجلد tmp
# if not os.path.exists('/tmp'):
#     os.makedirs('/tmp', exist_ok=True)

@app.route('/daily_report')
def daily_report():
    conn = get_db()
    cursor = conn.cursor()
    today = datetime.now().date()
    
    # تقرير الحضور اليومي
    cursor.execute("""
        SELECT teachers.name as teacher_name, attendance.class_name, 
               classrooms.name as classroom_name, attendance.entry_time
        FROM attendance
        JOIN teachers ON teachers.id = attendance.teacher_id
        JOIN classrooms ON classrooms.id = attendance.classroom_id
        WHERE DATE(attendance.entry_time) = ?
        ORDER BY attendance.entry_time DESC
    """, (today,))
    daily_attendance = cursor.fetchall()
    
    # تقرير المناوبة اليومي
    cursor.execute("""
        SELECT teachers.name as teacher_name, supervision.shift_type, 
               supervision.notes
        FROM supervision
        JOIN teachers ON teachers.id = supervision.teacher_id
        WHERE DATE(supervision.date) = ?
        ORDER BY supervision.shift_type
    """, (today,))
    daily_supervision = cursor.fetchall()
    
    conn.close()
    return render_template('daily_report.html', 
                         attendance=daily_attendance, 
                         supervision=daily_supervision,
                         date=today)

@app.route('/weekly_report')
def weekly_report():
    conn = get_db()
    cursor = conn.cursor()
    
    # حساب تاريخ بداية ونهاية الأسبوع
    today = datetime.now().date()
    start_of_week = today - timedelta(days=today.weekday())
    end_of_week = start_of_week + timedelta(days=6)
    
    # تقرير الحضور الأسبوعي
    cursor.execute("""
        SELECT 
            teachers.name as teacher_name,
            COUNT(*) as attendance_count,
            GROUP_CONCAT(DISTINCT classrooms.name) as classrooms
        FROM attendance
        JOIN teachers ON teachers.id = attendance.teacher_id
        JOIN classrooms ON classrooms.id = attendance.classroom_id
        WHERE DATE(attendance.entry_time) BETWEEN ? AND ?
        GROUP BY teachers.id, teachers.name
        ORDER BY attendance_count DESC
    """, (start_of_week, end_of_week))
    weekly_attendance = cursor.fetchall()
    
    # تقرير المناوبة الأسبوعي
    cursor.execute("""
        SELECT 
            teachers.name as teacher_name,
            COUNT(*) as supervision_count,
            GROUP_CONCAT(DISTINCT supervision.shift_type) as shift_types
        FROM supervision
        JOIN teachers ON teachers.id = supervision.teacher_id
        WHERE DATE(supervision.date) BETWEEN ? AND ?
        GROUP BY teachers.id, teachers.name
        ORDER BY supervision_count DESC
    """, (start_of_week, end_of_week))
    weekly_supervision = cursor.fetchall()
    
    conn.close()
    return render_template('weekly_report.html',
                         attendance=weekly_attendance,
                         supervision=weekly_supervision,
                         start_date=start_of_week,
                         end_date=end_of_week)

if __name__ == '__main__':
    app.run(debug=True)

if __name__ == '__main__':
    app.run(debug=True)

@app.route('/daily_report')
def daily_report():
    conn = get_db()
    cursor = conn.cursor()
    today = datetime.now().date()
    
    # تقرير الحضور اليومي
    cursor.execute("""
        SELECT teachers.name as teacher_name, attendance.class_name, 
               classrooms.name as classroom_name, attendance.entry_time
        FROM attendance
        JOIN teachers ON teachers.id = attendance.teacher_id
        JOIN classrooms ON classrooms.id = attendance.classroom_id
        WHERE DATE(attendance.entry_time) = ?
        ORDER BY attendance.entry_time DESC
    """, (today,))
    daily_attendance = cursor.fetchall()
    
    # تقرير المناوبة اليومي
    cursor.execute("""
        SELECT teachers.name as teacher_name, supervision.shift_type, 
               supervision.notes
        FROM supervision
        JOIN teachers ON teachers.id = supervision.teacher_id
        WHERE DATE(supervision.date) = ?
        ORDER BY supervision.shift_type
    """, (today,))
    daily_supervision = cursor.fetchall()
    
    conn.close()
    return render_template('daily_report.html', 
                         attendance=daily_attendance, 
                         supervision=daily_supervision,
                         date=today)

@app.route('/weekly_report')
def weekly_report():
    conn = get_db()
    cursor = conn.cursor()
    
    # حساب تاريخ بداية ونهاية الأسبوع
    today = datetime.now().date()
    start_of_week = today - timedelta(days=today.weekday())
    end_of_week = start_of_week + timedelta(days=6)
    
    # تقرير الحضور الأسبوعي
    cursor.execute("""
        SELECT 
            teachers.name as teacher_name,
            COUNT(*) as attendance_count,
            GROUP_CONCAT(DISTINCT classrooms.name) as classrooms
        FROM attendance
        JOIN teachers ON teachers.id = attendance.teacher_id
        JOIN classrooms ON classrooms.id = attendance.classroom_id
        WHERE DATE(attendance.entry_time) BETWEEN ? AND ?
        GROUP BY teachers.id, teachers.name
        ORDER BY attendance_count DESC
    """, (start_of_week, end_of_week))
    weekly_attendance = cursor.fetchall()
    
    # تقرير المناوبة الأسبوعي
    cursor.execute("""
        SELECT 
            teachers.name as teacher_name,
            COUNT(*) as supervision_count,
            GROUP_CONCAT(DISTINCT supervision.shift_type) as shift_types
        FROM supervision
        JOIN teachers ON teachers.id = supervision.teacher_id
        WHERE DATE(supervision.date) BETWEEN ? AND ?
        GROUP BY teachers.id, teachers.name
        ORDER BY supervision_count DESC
    """, (start_of_week, end_of_week))
    weekly_supervision = cursor.fetchall()
    
    conn.close()
    return render_template('weekly_report.html',
                         attendance=weekly_attendance,
                         supervision=weekly_supervision,
                         start_date=start_of_week,
                         end_date=end_of_week)

if __name__ == '__main__':
    app.run(debug=True)

if __name__ == '__main__':
    app.run(debug=True)

@app.route('/daily_report')
def daily_report():
    conn = get_db()
    cursor = conn.cursor()
    today = datetime.now().date()
    
    # تقرير الحضور اليومي
    cursor.execute("""
        SELECT teachers.name as teacher_name, attendance.class_name, 
               classrooms.name as classroom_name, attendance.entry_time
        FROM attendance
        JOIN teachers ON teachers.id = attendance.teacher_id
        JOIN classrooms ON classrooms.id = attendance.classroom_id
        WHERE DATE(attendance.entry_time) = ?
        ORDER BY attendance.entry_time DESC
    """, (today,))
    daily_attendance = cursor.fetchall()
    
    # تقرير المناوبة اليومي
    cursor.execute("""
        SELECT teachers.name as teacher_name, supervision.shift_type, 
               supervision.notes
        FROM supervision
        JOIN teachers ON teachers.id = supervision.teacher_id
        WHERE DATE(supervision.date) = ?
        ORDER BY supervision.shift_type
    """, (today,))
    daily_supervision = cursor.fetchall()
    
    conn.close()
    return render_template('daily_report.html', 
                         attendance=daily_attendance, 
                         supervision=daily_supervision,
                         date=today)

@app.route('/weekly_report')
def weekly_report():
    conn = get_db()
    cursor = conn.cursor()
    
    # حساب تاريخ بداية ونهاية الأسبوع
    today = datetime.now().date()
    start_of_week = today - timedelta(days=today.weekday())
    end_of_week = start_of_week + timedelta(days=6)
    
    # تقرير الحضور الأسبوعي
    cursor.execute("""
        SELECT 
            teachers.name as teacher_name,
            COUNT(*) as attendance_count,
            GROUP_CONCAT(DISTINCT classrooms.name) as classrooms
        FROM attendance
        JOIN teachers ON teachers.id = attendance.teacher_id
        JOIN classrooms ON classrooms.id = attendance.classroom_id
        WHERE DATE(attendance.entry_time) BETWEEN ? AND ?
        GROUP BY teachers.id, teachers.name
        ORDER BY attendance_count DESC
    """, (start_of_week, end_of_week))
    weekly_attendance = cursor.fetchall()
    
    # تقرير المناوبة الأسبوعي
    cursor.execute("""
        SELECT 
            teachers.name as teacher_name,
            COUNT(*) as supervision_count,
            GROUP_CONCAT(DISTINCT supervision.shift_type) as shift_types
        FROM supervision
        JOIN teachers ON teachers.id = supervision.teacher_id
        WHERE DATE(supervision.date) BETWEEN ? AND ?
        GROUP BY teachers.id, teachers.name
        ORDER BY supervision_count DESC
    """, (start_of_week, end_of_week))
    weekly_supervision = cursor.fetchall()
    
    conn.close()
    return render_template('weekly_report.html',
                         attendance=weekly_attendance,
                         supervision=weekly_supervision,
                         start_date=start_of_week,
                         end_date=end_of_week)

if __name__ == '__main__':
    app.run(debug=True)

if __name__ == '__main__':
    app.run(debug=True)

@app.route('/daily_report')
def daily_report():
    conn = get_db()
    cursor = conn.cursor()
    today = datetime.now().date()
    
    # تقرير الحضور اليومي
    cursor.execute("""
        SELECT teachers.name as teacher_name, attendance.class_name, 
               classrooms.name as classroom_name, attendance.entry_time
        FROM attendance
        JOIN teachers ON teachers.id = attendance.teacher_id
        JOIN classrooms ON classrooms.id = attendance.classroom_id
        WHERE DATE(attendance.entry_time) = ?
        ORDER BY attendance.entry_time DESC
    """, (today,))
    daily_attendance = cursor.fetchall()
    
    # تقرير المناوبة اليومي
    cursor.execute("""
        SELECT teachers.name as teacher_name, supervision.shift_type, 
               supervision.notes
        FROM supervision
        JOIN teachers ON teachers.id = supervision.teacher_id
        WHERE DATE(supervision.date) = ?
        ORDER BY supervision.shift_type
    """, (today,))
    daily_supervision = cursor.fetchall()
    
    conn.close()
    return render_template('daily_report.html', 
                         attendance=daily_attendance, 
                         supervision=daily_supervision,
                         date=today)

@app.route('/weekly_report')
def weekly_report():
    conn = get_db()
    cursor = conn.cursor()
    
    # حساب تاريخ بداية ونهاية الأسبوع
    today = datetime.now().date()
    start_of_week = today - timedelta(days=today.weekday())
    end_of_week = start_of_week + timedelta(days=6)
    
    # تقرير الحضور الأسبوعي
    cursor.execute("""
        SELECT 
            teachers.name as teacher_name,
            COUNT(*) as attendance_count,
            GROUP_CONCAT(DISTINCT classrooms.name) as classrooms
        FROM attendance
        JOIN teachers ON teachers.id = attendance.teacher_id
        JOIN classrooms ON classrooms.id = attendance.classroom_id
        WHERE DATE(attendance.entry_time) BETWEEN ? AND ?
        GROUP BY teachers.id, teachers.name
        ORDER BY attendance_count DESC
    """, (start_of_week, end_of_week))
    weekly_attendance = cursor.fetchall()
    
    # تقرير المناوبة الأسبوعي
    cursor.execute("""
        SELECT 
            teachers.name as teacher_name,
            COUNT(*) as supervision_count,
            GROUP_CONCAT(DISTINCT supervision.shift_type) as shift_types
        FROM supervision
        JOIN teachers ON teachers.id = supervision.teacher_id
        WHERE DATE(supervision.date) BETWEEN ? AND ?
        GROUP BY teachers.id, teachers.name
        ORDER BY supervision_count DESC
    """, (start_of_week, end_of_week))
    weekly_supervision = cursor.fetchall()
    
    conn.close()
    return render_template('weekly_report.html',
                         attendance=weekly_attendance,
                         supervision=weekly_supervision,
                         start_date=start_of_week,
                         end_date=end_of_week)

if __name__ == '__main__':
    app.run(debug=True)

if __name__ == '__main__':
    app.run(debug=True)

@app.route('/daily_report')
def daily_report():
    conn = get_db()
    cursor = conn.cursor()
    today = datetime.now().date()
    
    # تقرير الحضور اليومي
    cursor.execute("""
        SELECT teachers.name as teacher_name, attendance.class_name, 
               classrooms.name as classroom_name, attendance.entry_time
        FROM attendance
        JOIN teachers ON teachers.id = attendance.teacher_id
        JOIN classrooms ON classrooms.id = attendance.classroom_id
        WHERE DATE(attendance.entry_time) = ?
        ORDER BY attendance.entry_time DESC
    """, (today,))
    daily_attendance = cursor.fetchall()
    
    # تقرير المناوبة اليومي
    cursor.execute("""
        SELECT teachers.name as teacher_name, supervision.shift_type, 
               supervision.notes
        FROM supervision
        JOIN teachers ON teachers.id = supervision.teacher_id
        WHERE DATE(supervision.date) = ?
        ORDER BY supervision.shift_type
    """, (today,))
    daily_supervision = cursor.fetchall()
    
    conn.close()
    return render_template('daily_report.html', 
                         attendance=daily_attendance, 
                         supervision=daily_supervision,
                         date=today)

@app.route('/weekly_report')
def weekly_report():
    conn = get_db()
    cursor = conn.cursor()
    
    # حساب تاريخ بداية ونهاية الأسبوع
    today = datetime.now().date()
    start_of_week = today - timedelta(days=today.weekday())
    end_of_week = start_of_week + timedelta(days=6)
    
    # تقرير الحضور الأسبوعي
    cursor.execute("""
        SELECT 
            teachers.name as teacher_name,
            COUNT(*) as attendance_count,
            GROUP_CONCAT(DISTINCT classrooms.name) as classrooms
        FROM attendance
        JOIN teachers ON teachers.id = attendance.teacher_id
        JOIN classrooms ON classrooms.id = attendance.classroom_id
        WHERE DATE(attendance.entry_time) BETWEEN ? AND ?
        GROUP BY teachers.id, teachers.name
        ORDER BY attendance_count DESC
    """, (start_of_week, end_of_week))
    weekly_attendance = cursor.fetchall()
    
    # تقرير المناوبة الأسبوعي
    cursor.execute("""
        SELECT 
            teachers.name as teacher_name,
            COUNT(*) as supervision_count,
            GROUP_CONCAT(DISTINCT supervision.shift_type) as shift_types
        FROM supervision
        JOIN teachers ON teachers.id = supervision.teacher_id
        WHERE DATE(supervision.date) BETWEEN ? AND ?
        GROUP BY teachers.id, teachers.name
        ORDER BY supervision_count DESC
    """, (start_of_week, end_of_week))
    weekly_supervision = cursor.fetchall()
    
    conn.close()
    return render_template('weekly_report.html',
                         attendance=weekly_attendance,
                         supervision=weekly_supervision,
                         start_date=start_of_week,
                         end_date=end_of_week)

if __name__ == '__main__':
    app.run(debug=True)

if __name__ == '__main__':
    app.run(debug=True)

@app.route('/daily_report')
def daily_report():
    conn = get_db()
    cursor = conn.cursor()
    today = datetime.now().date()
    
    # تقرير الحضور اليومي
    cursor.execute("""
        SELECT teachers.name as teacher_name, attendance.class_name, 
               classrooms.name as classroom_name, attendance.entry_time
        FROM attendance
        JOIN teachers ON teachers.id = attendance.teacher_id
        JOIN classrooms ON classrooms.id = attendance.classroom_id
        WHERE DATE(attendance.entry_time) = ?
        ORDER BY attendance.entry_time DESC
    """, (today,))
    daily_attendance = cursor.fetchall()
    
    # تقرير المناوبة اليومي
    cursor.execute("""
        SELECT teachers.name as teacher_name, supervision.shift_type, 
               supervision.notes
        FROM supervision
        JOIN teachers ON teachers.id = supervision.teacher_id
        WHERE DATE(supervision.date) = ?
        ORDER BY supervision.shift_type
    """, (today,))
    daily_supervision = cursor.fetchall()
    
    conn.close()
    return render_template('daily_report.html', 
                         attendance=daily_attendance, 
                         supervision=daily_supervision,
                         date=today)

@app.route('/weekly_report')
def weekly_report():
    conn = get_db()
    cursor = conn.cursor()
    
    # حساب تاريخ بداية ونهاية الأسبوع
    today = datetime.now().date()
    start_of_week = today - timedelta(days=today.weekday())
    end_of_week = start_of_week + timedelta(days=6)
    
    # تقرير الحضور الأسبوعي
    cursor.execute("""
        SELECT 
            teachers.name as teacher_name,
            COUNT(*) as attendance_count,
            GROUP_CONCAT(DISTINCT classrooms.name) as classrooms
        FROM attendance
        JOIN teachers ON teachers.id = attendance.teacher_id
        JOIN classrooms ON classrooms.id = attendance.classroom_id
        WHERE DATE(attendance.entry_time) BETWEEN ? AND ?
        GROUP BY teachers.id, teachers.name
        ORDER BY attendance_count DESC
    """, (start_of_week, end_of_week))
    weekly_attendance = cursor.fetchall()
    
    # تقرير المناوبة الأسبوعي
    cursor.execute("""
        SELECT 
            teachers.name as teacher_name,
            COUNT(*) as supervision_count,
            GROUP_CONCAT(DISTINCT supervision.shift_type) as shift_types
        FROM supervision
        JOIN teachers ON teachers.id = supervision.teacher_id
        WHERE DATE(supervision.date) BETWEEN ? AND ?
        GROUP BY teachers.id, teachers.name
        ORDER BY supervision_count DESC
    """, (start_of_week, end_of_week))
    weekly_supervision = cursor.fetchall()
    
    conn.close()
    return render_template('weekly_report.html',
                         attendance=weekly_attendance,
                         supervision=weekly_supervision,
                         start_date=start_of_week,
                         end_date=end_of_week)

if __name__ == '__main__':
    app.run(debug=True)

# تعريف مسار قاعدة البيانات في مكان دائم
DATABASE = 'database.db'

def get_db():
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = sqlite3.connect(DATABASE)
        g.sqlite_db.row_factory = sqlite3.Row
    return g.sqlite_db

@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()

def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

# حذف الكود القديم الخاص بمجلد tmp
# if not os.path.exists('/tmp'):
#     os.makedirs('/tmp', exist_ok=True)

@app.route('/daily_report')
def daily_report():
    conn = get_db()
    cursor = conn.cursor()
    today = datetime.now().date()
    
    # تقرير الحضور اليومي
    cursor.execute("""
        SELECT teachers.name as teacher_name, attendance.class_name, 
               classrooms.name as classroom_name, attendance.entry_time
        FROM attendance
        JOIN teachers ON teachers.id = attendance.teacher_id
        JOIN classrooms ON classrooms.id = attendance.classroom_id
        WHERE DATE(attendance.entry_time) = ?
        ORDER BY attendance.entry_time DESC
    """, (today,))
    daily_attendance = cursor.fetchall()
    
    # تقرير المناوبة اليومي
    cursor.execute("""
        SELECT teachers.name as teacher_name, supervision.shift_type, 
               supervision.notes
        FROM supervision
        JOIN teachers ON teachers.id = supervision.teacher_id
        WHERE DATE(supervision.date) = ?
        ORDER BY supervision.shift_type
    """, (today,))
    daily_supervision = cursor.fetchall()
    
    conn.close()
    return render_template('daily_report.html', 
                         attendance=daily_attendance, 
                         supervision=daily_supervision,
                         date=today)

@app.route('/weekly_report')
def weekly_report():
    conn = get_db()
    cursor = conn.cursor()
    
    # حساب تاريخ بداية ونهاية الأسبوع
    today = datetime.now().date()
    start_of_week = today - timedelta(days=today.weekday())
    end_of_week = start_of_week + timedelta(days=6)
    
    # تقرير الحضور الأسبوعي
    cursor.execute("""
        SELECT 
            teachers.name as teacher_name,
            COUNT(*) as attendance_count,
            GROUP_CONCAT(DISTINCT classrooms.name) as classrooms
        FROM attendance
        JOIN teachers ON teachers.id = attendance.teacher_id
        JOIN classrooms ON classrooms.id = attendance.classroom_id
        WHERE DATE(attendance.entry_time) BETWEEN ? AND ?
        GROUP BY teachers.id, teachers.name
        ORDER BY attendance_count DESC
    """, (start_of_week, end_of_week))
    weekly_attendance = cursor.fetchall()
    
    # تقرير المناوبة الأسبوعي
    cursor.execute("""
        SELECT 
            teachers.name as teacher_name,
            COUNT(*) as supervision_count,
            GROUP_CONCAT(DISTINCT supervision.shift_type) as shift_types
        FROM supervision
        JOIN teachers ON teachers.id = supervision.teacher_id
        WHERE DATE(supervision.date) BETWEEN ? AND ?
        GROUP BY teachers.id, teachers.name
        ORDER BY supervision_count DESC
    """, (start_of_week, end_of_week))
    weekly_supervision = cursor.fetchall()
    
    conn.close()
    return render_template('weekly_report.html',
                         attendance=weekly_attendance,
                         supervision=weekly_supervision,
                         start_date=start_of_week,
                         end_date=end_of_week)

if __name__ == '__main__':
