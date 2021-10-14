from __future__ import annotations

import uuid
from typing import List
from fastapi.param_functions import Form
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel


class SignupRequest(BaseModel):
    email: str
    password: str

    class Config:
        schema_extra = {
            "example": {
                "email": "test@test.com",
                "password": "x0D32SaAi#5"
            }
        }


class SignupResponse(BaseModel):
    token: str

    class Config:
        schema_extra = {
            "example": {
                "token": "(JWT)"
            }
        }


class SignupConfirmRequest(BaseModel):
    token: str
    number: str

    class Config:
        schema_extra = {
            "example": {
                "token": "(JWT)",
                "number": "0123"
            }
        }


class LoginRequest:

    def __init__(
            self,
            grant_type: str = Form(None, regex="password|refresh_token"),
            username: str = Form(None),
            password: str = Form(None),
            refresh_token: str = Form(None)
    ):
        self.grant_type = grant_type
        self.username = username
        self.password = password
        self.refresh_token = refresh_token


class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = 'bearer'

    class Config:
        schema_extra = {
            "example": {
                "access_token": "(JWT)",
                "refresh_token": "(JWT)",
                'token_type': 'bearer'
            }
        }


class QuestionListItem(BaseModel):
    questionID: uuid.UUID
    title: str
    answeredCorrectly: bool

    class Config:
        schema_extra = {
            "example": {
                "questionID": '2f644942-e039-4a1c-aab2-bfb8d67d5ff9',
                "title": "add 2 value",
                "answeredCorrectly": False
            }
        }


class TestCase(BaseModel):
    input: str
    expected: str

    class Config:
        schema_extra = {
            "example": {
                "input": "(1, 2)",
                "expected": "3"
            }
        }


class Assertion(BaseModel):
    assertion: str
    message: str

    class Config:
        schema_extra = {
            "example": {
                "assertion": "'+' in code",
                "message": "加算が行われていない可能性があります"
            }
        }


class Question(BaseModel):
    questionID: uuid.UUID
    title: str
    description: str
    testCases: List[TestCase]
    assertions: List[Assertion]
    answeredCorrectly: bool
    defaultCode: str

    class Config:
        schema_extra = {
            "example": {
                "questionID": '2f644942-e039-4a1c-aab2-bfb8d67d5ff9',
                "title": "add 2 value",
                "description": "2つの値が与えられると、それらの値を足し合わせた数字を返す関数 `add` を定義してください。",
                "testCases": [
                    TestCase(input='(0, 0)', expected='0'),
                    TestCase(input='(1, 1)', expected='2'),
                    TestCase(input='(1.0, 1.0)', expected='2.0'),
                    TestCase(input='(-1, 1)', expected='0'),
                    TestCase(input='(-2, 1)', expected='-1')
                ],
                "assertions": [
                    Assertion(assertion="'+' in code", message='加算が行われていない可能性があります'),
                    Assertion(assertion="add(0, 0) === undefined", message='値が返却されていない可能性があります')
                ],
                "answeredCorrectly": False,
                "defaultCode": "function add2(first, second) {\n    // your code here\n\n}"
            }
        }


class UserAnswerRequest(BaseModel):
    questionID: uuid.UUID
    isCorrect: bool

    class Config:
        schema_extra = {
            "example": {
                "questionID": '2f644942-e039-4a1c-aab2-bfb8d67d5ff9',
                "isCorrect": False
            }
        }
