import sys
import os

# تحديد مسار التطبيق
project_dir = '/home/thoalbogadain/myapp'
if project_dir not in sys.path:
    sys.path.append(project_dir)

# استيراد التطبيق
from app import app as application

# تشغيل التطبيق محلياً للتطوير
if __name__ == "__main__":
    application.run()
