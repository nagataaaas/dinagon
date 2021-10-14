from typing import Optional, List, Tuple

from fastapi import HTTPException, status
from sqlalchemy import desc

from app.models import *


def get_active_user_by_email(email_address: str, session: Session) -> Optional[User]:
    return session.query(User).filter(User.email_address == email_address, User.is_active == True).one_or_none()


def get_user_by_id(id_: str, session: Session) -> Optional[User]:
    return session.query(User).get(uuid.UUID(id_))


def create_user(password_hash: str, salt: str, email_address: str, session: Session) -> User:
    user = User(email_address=email_address, password_hash=password_hash, salt=salt)
    session.add(user)
    session.commit()
    return user


def get_questions(user: User, session: Session) -> List[Tuple[Question, bool]]:
    answered_correctly = session.query(Answer) \
        .filter(Answer.user == user.id) \
        .order_by(desc(Answer.is_correct)) \
        .distinct(Answer.question) \
        .group_by(Answer.question) \
        .subquery()
    questions = session.query(Question, answered_correctly) \
        .outerjoin(answered_correctly, answered_correctly.c.question == Question.id) \
        .all()
    return [(q, any(ans)) for q, *ans in questions]


def get_question(user: User, question_id: uuid.UUID, session: Session) -> Tuple[Question, bool]:
    answered_correctly = session.query(Answer) \
        .filter(Answer.user == user.id) \
        .order_by(desc(Answer.is_correct)) \
        .distinct(Answer.question) \
        .group_by(Answer.question) \
        .subquery()
    q, *ans = session.query(Question, answered_correctly) \
        .outerjoin(answered_correctly, answered_correctly.c.question == Question.id) \
        .filter(Question.id == question_id) \
        .one_or_none()

    return q, any(ans)


def create_answer(user: User, question_id: uuid.UUID, is_correct: bool, failed_assertions: List[str], session: Session):
    question = session.query(Question).get(question_id)
    if not question:
        raise HTTPException(status.HTTP_404_NOT_FOUND)
    assertions = session.query(Assertion).filter(Assertion.id.in_([uuid.UUID(a) for a in failed_assertions])).all()
    if len(assertions) != len(failed_assertions):
        print('wo!')
        raise HTTPException(status.HTTP_400_BAD_REQUEST)

    answer = Answer(user=user.id, question=question_id, is_correct=is_correct, failed_assertions=assertions)

    session.add(answer)
    session.commit()
