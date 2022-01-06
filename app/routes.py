from fastapi import FastAPI, status, HTTPException, Depends, Cookie, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from app.config import PORT
from app.controller import (get_user_by_id, create_user,
                            get_questions, create_answer, get_question, get_answers, get_questions_by_id)
from app.models import get_db
from app.scheme import *
from itertools import chain

app = FastAPI(
    title='Dinagon',
    version='0.1 alpha',
    description='Server Side Api',
    servers=[{'url': 'http://localhost:{}/'.format(PORT), 'description': 'Development Server'},
             {'url': 'https://dinagon.herokuapp.com/', 'description': 'Heroku Server'}],
    debug=True
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)


@app.get('/question', response_model=List[QuestionListItem])
async def questions(response: Response, dinagon_user_token: Optional[str] = Cookie(None),
                    session: Session = Depends(get_db)):
    user = dinagon_user_token and get_user_by_id(dinagon_user_token, session)
    if not user:
        user = create_user(session)
        response.set_cookie(key='dinagon_user_token', value=user.id)

    return [QuestionListItem(questionID=q.id, title=q.title, answeredCorrectly=answered_correctly, level=q.level,
                             tags=[Tag(id=tag.id, name=tag.name, tutorial_link=tag.tutorial_link) for tag in q.tags])
            for q, answered_correctly in get_questions(user, session)]


@app.get('/question/{questionID}', response_model=Question)
async def certain_question(questionID: uuid.UUID, dinagon_user_token: str = Cookie(...),
                           session: Session = Depends(get_db)):
    user = get_user_by_id(dinagon_user_token, session)
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
                        Assertion(id=a.id,
                                  assertion=a.assertion,
                                  message=a.message,
                                  tags=[Tag(id=tag.id, name=tag.name, tutorial_link=tag.tutorial_link) for tag in
                                        a.tags])
                        for a in q.assertions
                    ],
                    answeredCorrectly=answered_correctly,
                    tags=[Tag(id=tag.id, name=tag.name, tutorial_link=tag.tutorial_link) for tag in q.tags],
                    level=q.level,
                    defaultCode=q.default_code)


@app.post('/answer', response_model=UserAnswerRequest, status_code=status.HTTP_201_CREATED)
async def answer(req: UserAnswerRequest, dinagon_user_token: str = Cookie(...), session: Session = Depends(get_db),
                 is_assertion_used: bool = True):
    user = get_user_by_id(dinagon_user_token, session)
    if not user:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED)

    create_answer(user, req.questionID, req.isCorrect, req.failedAssertions, is_assertion_used, session)


@app.get('/recommendation', response_model=RecommendationResponse)
async def recommendation(dinagon_user_token: str = Cookie(...), session: Session = Depends(get_db)):
    user = get_user_by_id(dinagon_user_token, session)
    if not user:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED)

    answers = get_answers(user, session)
    all_tags = list(chain.from_iterable([list(chain.from_iterable(a.tags for a in question.assertions)) for question in
                                         get_questions_by_id([ans.question for ans in answers], session)]))
    wrong_tags = list(chain.from_iterable(
        [list(chain.from_iterable(a.tags for a in ans.failed_assertions)) for ans in answers if
         ans.is_correct is False]))

    result = []

    for tag in set(all_tags):
        wrong_ratio = wrong_tags.count(tag) / len(wrong_tags)
        if wrong_ratio > 0:
            tag_ratio = all_tags.count(tag) / len(all_tags)
            result.append((-wrong_ratio / tag_ratio, tag))

    result.sort()
    return RecommendationResponse(tags=[Tag(id=t.id, name=t.name, tutorial_link=t.tutorial_link) for _, t in result])


@app.get('/openapi/yaml', response_class=HTMLResponse, include_in_schema=False)
async def openapi_yaml():
    import yaml
    data = app.openapi()
    for i, v in enumerate(data['servers']):
        data['servers'][i]['url'] = str(v['url'])
    yaml_data = yaml.dump(data, encoding='utf-8', allow_unicode=True, sort_keys=False).decode()
    return HTMLResponse('<html><head><meta charset="utf-8"/></head><body>'
                        '<textarea rows="100" cols="200">{}</textarea></body></html>'.format(yaml_data))
