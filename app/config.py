import os

IS_LOCAL = os.path.exists('.LOCAL')
IS_MOCK = False
HTML_DIR = 'app/templates'
DATABASE_URI = 'sqlite:///database.db'

HOST = '0.0.0.0'
PORT = int(os.environ.get('PORT', 8888))
