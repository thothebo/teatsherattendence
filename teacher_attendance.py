import sqlite3
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox

class TeacherAttendanceSystem:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("نظام متابعة دخول المعلمين")
        self.root.geometry("800x600")
        
        # إنشاء قاعدة البيانات
        self.create_database()
        
        # إنشاء واجهة المستخدم
        self.create_gui()
    
    def create_database(self):
        self.conn = sqlite3.connect('school_attendance.db')
        self.cursor = self.conn.cursor()
        
        # إنشاء جدول المعلمين
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS teachers (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL
            )
        ''')
        
        # إنشاء جدول الحضور
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS attendance (
                id INTEGER PRIMARY KEY,
                teacher_id INTEGER,
                class_name TEXT,
                entry_time DATETIME,
                FOREIGN KEY (teacher_id) REFERENCES teachers (id)
            )
        ''')
        
        self.conn.commit()
    
    def create_gui(self):
        # إطار إضافة معلم جديد
        teacher_frame = ttk.LabelFrame(self.root, text="إضافة معلم جديد")
        teacher_frame.pack(padx=10, pady=5, fill="x")
        
        ttk.Label(teacher_frame, text="اسم المعلم:").grid(row=0, column=1, padx=5, pady=5)
        self.teacher_name = ttk.Entry(teacher_frame)
        self.teacher_name.grid(row=0, column=0, padx=5, pady=5)
        ttk.Button(teacher_frame, text="إضافة معلم", command=self.add_teacher).grid(row=0, column=2, padx=5, pady=5)
        
        # إطار تسجيل الحضور
        attendance_frame = ttk.LabelFrame(self.root, text="تسجيل الحضور")
        attendance_frame.pack(padx=10, pady=5, fill="x")
        
        ttk.Label(attendance_frame, text="المعلم:").grid(row=0, column=1, padx=5, pady=5)
        self.teacher_select = ttk.Combobox(attendance_frame)
        self.teacher_select.grid(row=0, column=0, padx=5, pady=5)
        
        ttk.Label(attendance_frame, text="الحصة:").grid(row=1, column=1, padx=5, pady=5)
        self.class_name = ttk.Entry(attendance_frame)
        self.class_name.grid(row=1, column=0, padx=5, pady=5)
        
        ttk.Button(attendance_frame, text="تسجيل الدخول", command=self.record_attendance).grid(row=2, column=0, columnspan=2, pady=10)
        
        # جدول عرض السجلات
        self.tree = ttk.Treeview(self.root, columns=("المعلم", "الحصة", "وقت الدخول"), show="headings")
        self.tree.heading("المعلم", text="المعلم")
        self.tree.heading("الحصة", text="الحصة")
        self.tree.heading("وقت الدخول", text="وقت الدخول")
        self.tree.pack(padx=10, pady=5, fill="both", expand=True)
        
        self.update_teacher_list()
        self.update_attendance_list()
    
    def add_teacher(self):
        name = self.teacher_name.get()
        if name:
            self.cursor.execute("INSERT INTO teachers (name) VALUES (?)", (name,))
            self.conn.commit()
            self.teacher_name.delete(0, tk.END)
            self.update_teacher_list()
            messagebox.showinfo("نجاح", "تم إضافة المعلم بنجاح")
        else:
            messagebox.showerror("خطأ", "الرجاء إدخال اسم المعلم")
    
    def record_attendance(self):
        teacher = self.teacher_select.get()
        class_name = self.class_name.get()
        
        if teacher and class_name:
            self.cursor.execute("SELECT id FROM teachers WHERE name=?", (teacher,))
            teacher_id = self.cursor.fetchone()[0]
            
            self.cursor.execute("""
                INSERT INTO attendance (teacher_id, class_name, entry_time)
                VALUES (?, ?, ?)
            """, (teacher_id, class_name, datetime.now()))
            
            self.conn.commit()
            self.class_name.delete(0, tk.END)
            self.update_attendance_list()
            messagebox.showinfo("نجاح", "تم تسجيل الحضور بنجاح")
        else:
            messagebox.showerror("خطأ", "الرجاء إكمال جميع البيانات المطلوبة")
    
    def update_teacher_list(self):
        self.cursor.execute("SELECT name FROM teachers")
        teachers = [row[0] for row in self.cursor.fetchall()]
        self.teacher_select['values'] = teachers
    
    def update_attendance_list(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        self.cursor.execute("""
            SELECT teachers.name, attendance.class_name, attendance.entry_time
            FROM attendance
            JOIN teachers ON teachers.id = attendance.teacher_id
            ORDER BY attendance.entry_time DESC
        """)
        
        for row in self.cursor.fetchall():
            self.tree.insert("", "end", values=row)
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = TeacherAttendanceSystem()
    app.run()