import sys

sys.path.insert(0, '/var/www/html/RasPiServer/RasPiServer.wsgi')
sys.path.insert(0, '/var/www/html/RasPiServer')

from RasPiServer import app
