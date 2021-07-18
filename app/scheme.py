from __future__ import annotations

import uuid
from typing import List

from pydantic import BaseModel


class LoginRequest(BaseModel):
    displayID: str
    password: str

    class Config:
        schema_extra = {
            "example": {
                "displayID": "IamTestUser0123",
                "password": "x0D32SaAi#5"
            }
        }


class RefreshRequest(BaseModel):
    refreshToken: str

    class Config:
        schema_extra = {
            "example": {
                "refreshToken": "(JWT)"
            }
        }


class TokenBodyRequest(BaseModel):
    sessionToken: str

    class Config:
        schema_extra = {
            "example": {
                "sessionToken": "(JWT)"
            }
        }


class LoginResponse(BaseModel):
    sessionToken: str
    refreshToken: str

    class Config:
        schema_extra = {
            "example": {
                "sessionToken": "(JWT)",
                "refreshToken": "(JWT)"
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
                "input": "add(1, 2)",
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

    class Config:
        schema_extra = {
            "example": {
                "questionID": '2f644942-e039-4a1c-aab2-bfb8d67d5ff9',
                "title": "add 2 value",
                "description": "2つの値が与えられると、それらの値を足し合わせた数字を返す関数 `add` を定義してください。",
                "testCases": [
                    TestCase(input='add(0, 0)', expected='0'),
                    TestCase(input='add(1, 1)', expected='2'),
                    TestCase(input='add(1.0, 1.0)', expected='2.0'),
                    TestCase(input='add(-1, 1)', expected='0'),
                    TestCase(input='add(-2, 1)', expected='-1')
                ],
                "assertions": [
                    Assertion(assertion="'+' in code", message='加算が行われていない可能性があります'),
                    Assertion(assertion="add(0, 0) === undefined", message='値が返却されていない可能性があります')
                ],
                "answeredCorrectly": False,
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
