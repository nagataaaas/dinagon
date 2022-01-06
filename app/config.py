import os

IS_LOCAL = os.path.exists('.LOCAL')
IS_MOCK = False
IS_DEV = True
HTML_DIR = 'app/templates'
DATABASE_URI = 'mysql://be465100597ebc:e489c1f8@us-cdbr-east-05.cleardb.net/heroku_d5fccd003aef2db'

HOST = '0.0.0.0'
PORT = int(os.environ.get('PORT', 8888))
