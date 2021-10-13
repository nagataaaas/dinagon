import os
from collections import namedtuple

MailConfig = namedtuple('mail_config', ['host', 'port', 'address', 'password'])
MAIL = MailConfig(host=os.environ['MAIL_SERVER'], port=int(os.environ['MAIL_PORT']),
                  address=os.environ['MAIL_ADDRESS'], password=os.environ['MAIL_PASS'])

JWT_SECRET = os.environ['JWT_SECRET']
