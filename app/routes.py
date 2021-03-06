from itertools import chain
from typing import Optional

from fastapi import FastAPI, status, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, FileResponse
from sqlalchemy.orm import Session

from app.config import PORT, DATABASE_URI
from app.controller import (get_user_by_id, create_user,
                            get_questions, create_answer, get_question, get_answers, get_questions_by_id)
from app.models import get_db
from app.scheme import *

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
    allow_origins=['https://chunagon.herokuapp.com', 'https://chunagon-dash.herokuapp.com',
                   'http://chunagon.herokuapp.com', 'http://chunagon-dash.herokuapp.com', 'http://localhost:3000'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)


@app.get('/question', response_model=QuestionList)
async def questions(token: Optional[str] = '', session: Session = Depends(get_db)):
    user = token and get_user_by_id(token, session)
    if not user:
        user = create_user(session)

    return QuestionList(token=user.id,
                        questions=[QuestionListItem(questionID=q.id, title=q.title,
                                                    answeredCorrectly=answered_correctly, level=q.level,
                                                    tags=[Tag(id=tag.id, name=tag.name, tutorial_link=tag.tutorial_link)
                                                          for tag in q.tags])
                                   for q, answered_correctly in get_questions(user, session)])


@app.get('/question/{questionID}', response_model=Question)
async def certain_question(questionID: uuid.UUID, token: str, session: Session = Depends(get_db)):
    user = get_user_by_id(token, session)
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
async def answer(req: UserAnswerRequest, token: str, session: Session = Depends(get_db),
                 is_assertion_used: bool = True):
    user = get_user_by_id(token, session)
    if not user:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED)

    create_answer(user, req.questionID, req.isCorrect, req.failedAssertions, is_assertion_used, session)


@app.get('/recommendation', response_model=RecommendationResponse)
async def recommendation(token: str, session: Session = Depends(get_db)):
    user = get_user_by_id(token, session)
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


@app.get('/download/database')
async def download_database():
    return FileResponse(DATABASE_URI.split('/')[-1])
