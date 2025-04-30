from app import app

if __name__ == "__main__":
    app.run()
import sys
path = '/home/yourusername/myapp'
if path not in sys.path:
    sys.path.append(path)

from app import app as application
