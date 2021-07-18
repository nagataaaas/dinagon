import datetime

import jwt
from fastapi import status, HTTPException

from app.config import JWT_SECRET


def encode_jwt(payload: dict) -> str:
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")


def decode_jwt(jwt_value: str) -> dict:
    return jwt.decode(jwt_value, key=JWT_SECRET, algorithms=['HS256'])


def is_expired(jwt_value: dict) -> bool:
    return datetime.datetime.fromtimestamp(jwt_value['expired']) < datetime.datetime.now()


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
