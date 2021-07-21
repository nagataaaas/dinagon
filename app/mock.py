import datetime

from fastapi import FastAPI, status, BackgroundTasks, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from jinja2 import Environment, FileSystemLoader

from app.config import PORT
from app.scheme import *
from app.utils import (encode_jwt, parse_session_token, parse_refresh_token, random_number, send_account_creation_mail,
                       parse_token, hash_password, create_token)

app = FastAPI(
    title='Dinagon',
    version='0.1 alpha',
    description='Server Side Mock Api',
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
async def signup(req: SignupRequest, background_tasks: BackgroundTasks):
    number = random_number()
    
    text = env.get_template('account_creation_mail.txt').render({'auth_number': number})
    html = env.get_template('account_creation_mail.html').render({'auth_number': number})
    background_tasks.add_task(send_account_creation_mail, req.email, text, html)
    
    token = encode_jwt({'email': req.email,
                        'password': hash_password(req.password),
                        'number': number,
                        'expired': (datetime.datetime.now() + datetime.timedelta(minutes=20)).timestamp()})
    return SignupResponse(token=token)


@app.post('/signup/confirm', response_model=LoginResponse)
async def signup_confirm(req: SignupConfirmRequest):
    payload = parse_token(req.token)
    if payload['number'] != req.number:
        raise HTTPException(status.HTTP_400_BAD_REQUEST)

    session_token, refresh_token = create_token(payload['email'])

    return LoginResponse(sessionToken=session_token, refreshToken=refresh_token)


@app.post('/login', response_model=LoginResponse)
async def login(req: LoginRequest):
    session_token, refresh_token = create_token(req.email)

    return LoginResponse(sessionToken=session_token, refreshToken=refresh_token)


@app.post('/login/refresh', response_model=LoginResponse)
async def login_refresh(req: RefreshRequest):
    payload = parse_refresh_token(req.refreshToken)
    session_token, refresh_token = create_token(payload['email'])
    return LoginResponse(sessionToken=session_token, refreshToken=refresh_token)


@app.get('/question', response_model=List[QuestionListItem])
async def questions(sessionToken: str):
    payload = parse_session_token(sessionToken)

    print(payload)
    return [
        QuestionListItem(questionID=uuid.uuid4(),
                         title='add 2', answeredCorrectly=False),
        QuestionListItem(questionID=uuid.uuid4(),
                         title='add 3', answeredCorrectly=True),
    ]


@app.get('/question/{questionID}', response_model=Question)
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
                        Assertion(assertion="'+' in code",
                                  message='加算が行われていない可能性があります'),
                        Assertion(assertion="add(0, 0) === undefined",
                                  message='値が返却されていない可能性があります')
                    ],
                    answeredCorrectly=False)


@app.post('/answer', response_model=UserAnswerRequest, status_code=status.HTTP_201_CREATED)
async def questions(sessionToken: str, req: UserAnswerRequest):
    _ = parse_session_token(sessionToken)
    print(req)


@app.get('/openapi/yaml', response_class=HTMLResponse, include_in_schema=False)
async def openapi_yaml():
    import yaml
    data = app.openapi()
    for i, v in enumerate(data['servers']):
        data['servers'][i]['url'] = str(v['url'])
    yaml_data = yaml.dump(data, encoding='utf-8', allow_unicode=True, sort_keys=False).decode()
    return HTMLResponse('<html><head><meta charset="utf-8"/></head><body>'
                        '<textarea rows="100" cols="200">{}</textarea></body></html>'.format(yaml_data))
