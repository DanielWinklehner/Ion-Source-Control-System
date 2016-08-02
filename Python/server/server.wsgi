import sys

sys.path.insert(0, '/var/www/html/Ion-Source-Control-System/Python/server/server.wsgi')
sys.path.insert(0, '/var/www/html/Ion-Source-Control-System/Python/server')

from server import app as application
