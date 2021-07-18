import os
import uuid

IS_LOCAL = os.path.exists('.LOCAL')
HTML_DIR = 'app/templates'
JWT_SECRET = uuid.uuid4().hex

HOST = '0.0.0.0'
PORT = 8888
