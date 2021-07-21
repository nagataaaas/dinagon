import datetime

from fastapi import FastAPI, status, BackgroundTasks, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from jinja2 import Environment, FileSystemLoader
from sqlalchemy.orm import Session
from app.config import PORT
from app.scheme import *
from app.utils import (encode_jwt, parse_session_token, parse_refresh_token, random_number, send_account_creation_mail,
                       parse_token, hash_password, create_token)
from app.models import get_db
from app.controller import (get_active_user_by_email, get_user_by_id, create_user,
                            get_questions, create_answer, get_question)

app = FastAPI(
    title='Dinagon',
    version='0.1 alpha',
    description='Server Side Api',
    servers=[{'url': 'http://localhost:{}/'.format(PORT), 'description': 'Development Server'}],
    debug=True
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

app.mount('/static', StaticFiles(directory='app/static'), name='static')

env = Environment(loader=FileSystemLoader('app/static/templates'))


@app.post('/signup', response_model=SignupResponse)
async def signup(req: SignupRequest, background_tasks: BackgroundTasks, session: Session = Depends(get_db)):
    number = random_number()

    if get_active_user_by_email(req.email, session):
        raise HTTPException(status.HTTP_409_CONFLICT)

    text = env.get_template('account_creation_mail.txt').render({'auth_number': number})
    html = env.get_template('account_creation_mail.html').render({'auth_number': number})
    background_tasks.add_task(send_account_creation_mail, req.email, text, html)

    password, salt = hash_password(req.password)
    token = encode_jwt({'email': req.email,
                        'password': password,
                        'salt': salt,
                        'number': number,
                        'expired': (datetime.datetime.now() + datetime.timedelta(minutes=20)).timestamp()})
    return SignupResponse(token=token)


@app.post('/signup/confirm', response_model=LoginResponse)
async def signup_confirm(req: SignupConfirmRequest, session: Session = Depends(get_db)):
    payload = parse_token(req.token)
    if payload['number'] != req.number:
        raise HTTPException(status.HTTP_400_BAD_REQUEST)
    if get_active_user_by_email(payload['email'], session):
        raise HTTPException(status.HTTP_409_CONFLICT)

    user = create_user(payload['password'], payload['salt'], payload['email'], session)
    session_token, refresh_token = create_token(user.id.hex)

    return LoginResponse(sessionToken=session_token, refreshToken=refresh_token)


@app.post('/login', response_model=LoginResponse)
async def login(req: LoginRequest, session: Session = Depends(get_db)):
    user = get_active_user_by_email(req.email, session)

    if not user or hash_password(req.password, user.salt)[0] != user.password_hash:
        raise HTTPException(status.HTTP_400_BAD_REQUEST)

    session_token, refresh_token = create_token(user.id.hex)

    return LoginResponse(sessionToken=session_token, refreshToken=refresh_token)


@app.post('/login/refresh', response_model=LoginResponse)
async def login_refresh(req: RefreshRequest, session: Session = Depends(get_db)):
    payload = parse_refresh_token(req.refreshToken)

    if not get_user_by_id(payload['id'], session):
        raise HTTPException(status.HTTP_400_BAD_REQUEST)

    session_token, refresh_token = create_token(payload['id'])
    return LoginResponse(sessionToken=session_token, refreshToken=refresh_token)


@app.get('/question', response_model=List[QuestionListItem])
async def questions(sessionToken: str, session: Session = Depends(get_db)):
    payload = parse_session_token(sessionToken)

    user = get_user_by_id(payload['id'], session)
    if not user:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED)

    return [QuestionListItem(questionID=q.id, title=q.title, answeredCorrectly=answered_correctly) for
            q, answered_correctly in get_questions(user, session)]


@app.get('/question/{questionID}', response_model=Question)
async def curtain_question(sessionToken: str, questionID: uuid.UUID,  session: Session = Depends(get_db)):
    payload = parse_session_token(sessionToken)

    user = get_user_by_id(payload['id'], session)
    if not user:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED)
    q, answered_correctly = get_question(user, questionID, session)

    return Question(questionID=q.id, title=q.title,
                    description=q.description,
                    testCases=[
                        TestCase(input=t.input, expected=t.expected)
                        for t in q.test_cases
                    ],
                    assertions=[
                        Assertion(assertion=a.assertion,
                                  message=a.message)
                        for a in q.assertions
                    ],
                    answeredCorrectly=answered_correctly)


@app.post('/answer', response_model=UserAnswerRequest, status_code=status.HTTP_201_CREATED)
async def answer(req: UserAnswerRequest, session: Session = Depends(get_db)):
    payload = parse_session_token(req.sessionToken)

    user = get_user_by_id(payload['id'], session)
    if not user:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED)

    create_answer(user, req.questionID, req.isCorrect, session)


@app.get('/openapi/yaml', response_class=HTMLResponse, include_in_schema=False)
async def openapi_yaml():
    import yaml
    data = app.openapi()
    for i, v in enumerate(data['servers']):
        data['servers'][i]['url'] = str(v['url'])
    yaml_data = yaml.dump(data, encoding='utf-8', allow_unicode=True, sort_keys=False).decode()
    return HTMLResponse('<html><head><meta charset="utf-8"/></head><body>'
                        '<textarea rows="100" cols="200">{}</textarea></body></html>'.format(yaml_data))
