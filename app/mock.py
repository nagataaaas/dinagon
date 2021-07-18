import datetime

from fastapi import FastAPI, status
from fastapi.staticfiles import StaticFiles

from app.scheme import *
from app.utils import encode_jwt, parse_session_token, parse_refresh_token
import uuid

api = FastAPI(
    title='Dinagon',
    version='0.1 alpha',
    description='Server Side Api',
    debug=True
)
api.mount('/static', StaticFiles(directory='app/static'), name='static')


@api.post('/login', response_model=LoginResponse)
async def login(req: LoginRequest):
    session_token = encode_jwt({'userID': req.displayID,
                                'expired': (datetime.datetime.now() + datetime.timedelta(days=1)).timestamp(),
                                'type': 'session'})
    refresh_token = encode_jwt({'userID': req.displayID,
                                'expired': (datetime.datetime.now() + datetime.timedelta(days=7)).timestamp(),
                                'type': 'refresh'})

    return LoginResponse(sessionToken=session_token, refreshToken=refresh_token)


@api.post('/login/refresh', response_model=LoginResponse)
async def login_refresh(req: RefreshRequest):
    payload = parse_refresh_token(req.refreshToken)
    session_token = encode_jwt({'userID': payload['userID'],
                                'expired': (datetime.datetime.now() + datetime.timedelta(days=1)).timestamp(),
                                'type': 'session'})
    refresh_token = encode_jwt({'userID': payload['userID'],
                                'expired': (datetime.datetime.now() + datetime.timedelta(days=7)).timestamp(),
                                'type': 'refresh'})
    return LoginResponse(sessionToken=session_token, refreshToken=refresh_token)


@api.get('/question', response_model=List[QuestionListItem])
async def questions(sessionToken: str):
    payload = parse_session_token(sessionToken)

    print(payload)
    return [
        QuestionListItem(questionID=uuid.uuid4(), title='add 2', answeredCorrectly=False),
        QuestionListItem(questionID=uuid.uuid4(), title='add 3', answeredCorrectly=True),
    ]


@api.get('/question/{questionID}', response_model=Question)
async def questions(sessionToken: str, questionID: uuid.UUID):
    payload = parse_session_token(sessionToken)
    print(questionID)
    print(payload)

    return Question(questionID=questionID, title='add 2',
                    description="2つの値が与えられると、それらの値を足し合わせた数字を返す関数 `add` を定義してください。",
                    testCases=[
                        TestCase(input='add(0, 0)', expected='0'),
                        TestCase(input='add(1, 1)', expected='2'),
                        TestCase(input='add(1.0, 1.0)', expected='2.0'),
                        TestCase(input='add(-1, 1)', expected='0'),
                        TestCase(input='add(-2, 1)', expected='-1')
                    ],
                    assertions=[
                        Assertion(assertion="'+' in code", message='加算が行われていない可能性があります'),
                        Assertion(assertion="add(0, 0) === undefined", message='値が返却されていない可能性があります')
                    ],
                    answeredCorrectly=False)


@api.post('/answer', response_model=UserAnswerRequest, status_code=status.HTTP_201_CREATED)
async def questions(sessionToken: str, req: UserAnswerRequest):
    _ = parse_session_token(sessionToken)
    print(req)
