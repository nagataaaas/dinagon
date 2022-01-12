from typing import Optional, List, Tuple

from fastapi import HTTPException, status
from sqlalchemy import desc
from sqlalchemy.sql import func

from app.models import *


def get_user_by_id(id_: str, session: Session) -> Optional[User]:
    return session.query(User).get(uuid.UUID(id_))


def create_user(session: Session) -> User:
    user = User()
    session.add(user)
    session.commit()
    return user


def get_questions(user: User, session: Session) -> List[Tuple[Question, bool]]:
    answered_correctly = session.query(func.max(Answer.is_correct), Answer.question) \
        .filter(Answer.user == user.id) \
        .group_by(Answer.question) \
        .subquery()
    questions = session.query(Question, answered_correctly) \
        .outerjoin(answered_correctly, answered_correctly.c.question == Question.id) \
        .all()

    return [(q, ans[0] is True) for q, *ans in questions]


def get_question(user: User, question_id: uuid.UUID, session: Session) -> Tuple[Question, bool]:
    answered_correctly = session.query(func.max(Answer.is_correct), Answer.question) \
        .filter(Answer.user == user.id) \
        .group_by(Answer.question) \
        .subquery()
    q, *ans = session.query(Question, answered_correctly) \
        .outerjoin(answered_correctly, answered_correctly.c.question == Question.id) \
        .filter(Question.id == question_id) \
        .one_or_none()

    return q, ans[0] is True


def get_questions_by_id(question_ids: List[uuid.UUID], session: Session) -> List[Question]:
    return session.query(Question).filter(Question.id.in_(question_ids)).all()


def get_answers(user: User, session: Session) -> List[Answer]:
    answers = session.query(Answer) \
        .filter(Answer.user == user.id) \
        .order_by(desc(Answer.is_correct)) \
        .subquery()
    q = session.query() \
        .add_entity(Answer, alias=answers).group_by(answers.c.question) \
        .all()

    return q


def create_answer(user: User, question_id: uuid.UUID, is_correct: bool, failed_assertions: List[uuid.UUID],
                  is_assertion_used: bool, session: Session):
    question = session.query(Question).get(question_id)
    if not question:
        raise HTTPException(status.HTTP_404_NOT_FOUND)
    assertions = session.query(Assertion).filter(Assertion.id.in_([a for a in failed_assertions])).all()
    if len(assertions) != len(failed_assertions):
        raise HTTPException(status.HTTP_400_BAD_REQUEST)

    answer = Answer(user=user.id, question=question_id, is_correct=is_correct, failed_assertions=assertions,
                    use_assertions=is_assertion_used)

    session.add(answer)
    session.commit()
