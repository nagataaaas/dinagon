import base64
import datetime
import hashlib
import os
import random
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Optional

import jwt
from fastapi import status, HTTPException

from app.config import JWT_SECRET
from app.secrets import MAIL


def encode_jwt(payload: dict) -> str:
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")


def decode_jwt(jwt_value: str) -> dict:
    return jwt.decode(jwt_value, key=JWT_SECRET, algorithms=['HS256'])


def is_expired(jwt_value: dict) -> bool:
    return datetime.datetime.fromtimestamp(jwt_value['expired']) < datetime.datetime.now()


def parse_token(jwt_value: str) -> dict:
    if jwt_value is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED)
    payload = decode_jwt(jwt_value)
    return payload


def create_token(email: str) -> (str, str):
    return (encode_jwt({'email': email,
                        'expired': (datetime.datetime.now() + datetime.timedelta(days=1)).timestamp(),
                        'type': 'session'}),
            encode_jwt({'email': email,
                        'expired': (datetime.datetime.now() + datetime.timedelta(days=7)).timestamp(),
                        'type': 'refresh'}))


def parse_session_token(jwt_value: str) -> dict:
    if jwt_value is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED)
    payload = decode_jwt(jwt_value)
    if is_expired(payload) or payload.get('type') != 'session':
        raise HTTPException(status.HTTP_401_UNAUTHORIZED)
    return payload


def parse_refresh_token(jwt_value: str) -> dict:
    if jwt_value is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED)
    payload = decode_jwt(jwt_value)
    if is_expired(payload) or payload.get('type') != 'refresh':
        raise HTTPException(status.HTTP_401_UNAUTHORIZED)
    return payload


def random_number(digit: int = 4) -> str:
    return '{:>04}'.format(random.randint(1, 10 ** digit - 1))


def send_account_creation_mail(to: str, text: str, html: str) -> None:
    msg = MIMEMultipart('alternative')
    msg['Subject'] = "【Dinagon】登録確認コード"
    msg['From'] = MAIL.address
    msg['To'] = to

    part1 = MIMEText(text, 'plain')
    part2 = MIMEText(html, 'html')

    msg.attach(part1)
    msg.attach(part2)
    server = smtplib.SMTP_SSL("smtp.gmail.com", 465,
                              context=ssl.create_default_context())
    server.login(MAIL.address, MAIL.password)
    server.send_message(msg)  # メールの送信


def hash_password(password: str, salt: Optional[str] = None):
    if salt is None:
        salt = base64.b64encode(os.urandom(32)).hex()

    library_hashed = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 1000)
    return library_hashed.hex(), salt
