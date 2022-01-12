import os

IS_LOCAL = os.path.exists('.LOCAL')
IS_DEV = True
HTML_DIR = 'app/templates'
DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///database.db')

HOST = '0.0.0.0'
PORT = int(os.environ.get('PORT', 8888))
