import datetime
import uuid
from typing import Generator

from sqlalchemy import Column, Boolean, ForeignKey, DateTime, Table, Text, Integer
from sqlalchemy import MetaData
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.orm.session import Session
from sqlalchemy_utils import UUIDType
import app.config

meta = MetaData()

engine = create_engine(
    app.config.DATABASE_URI,
    encoding='utf-8',
    pool_recycle=60,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def clear_database():
    Base.metadata.drop_all(engine)


def create_database():
    Base.metadata.create_all(bind=engine)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


assertion_tag_relation = Table('assertion_tag_relation', Base.metadata,
                               Column('assertion_id', UUIDType(binary=False), ForeignKey('assertions.id'),
                                      primary_key=True),
                               Column('tag_id', UUIDType(binary=False), ForeignKey('tags.id'), primary_key=True)
                               )
question_tag_relation = Table('question_tag_relation', Base.metadata,
                              Column('question_id', UUIDType(binary=False), ForeignKey('questions.id'),
                                     primary_key=True),
                              Column('tag_id', UUIDType(binary=False), ForeignKey('tags.id'), primary_key=True)
                              )
answer_assertion_relation = Table('answer_assertion_relation', Base.metadata,
                                  Column('answer_id', UUIDType(binary=False), ForeignKey('answers.id'),
                                         primary_key=True),
                                  Column('assertion_id', UUIDType(binary=False), ForeignKey('assertions.id'),
                                         primary_key=True)
                                  )


class User(Base):
    __tablename__ = 'users'

    id = Column(UUIDType(binary=False), primary_key=True, default=uuid.uuid4)

    def __repr__(self):
        return f'Users(id={self.id!r})'


class Answer(Base):
    __tablename__ = 'answers'

    id = Column(UUIDType(binary=False), primary_key=True, default=uuid.uuid4)

    user = Column(UUIDType(binary=False), ForeignKey('users.id'))
    question = Column(UUIDType(binary=False), ForeignKey('questions.id'))

    is_correct = Column(Boolean, nullable=False)

    failed_assertions = relationship("Assertion", secondary=answer_assertion_relation)

    use_assertions = Column(Boolean, nullable=False)

    timestamp = Column(DateTime, default=datetime.datetime.now)

    def __repr__(self):
        return (f'Answers(id={self.id!r}, user={self.user!r}, question={self.question!r}, '
                f'is_correct={self.is_correct}, timestamp={self.timestamp!r})')


class Question(Base):
    __tablename__ = 'questions'

    id = Column(UUIDType(binary=False), primary_key=True, default=uuid.uuid4)

    title = Column(Text, nullable=False)
    description = Column(Text, nullable=False)
    default_code = Column(Text, nullable=False)

    test_cases = relationship('TestCase', uselist=True, lazy='dynamic')
    assertions = relationship('Assertion', uselist=True, lazy='dynamic')

    level = Column(Integer, nullable=False)

    tags = relationship('Tag', secondary=question_tag_relation)

    def __repr__(self):
        return (f'Question(id={self.id!r}, title={self.title!r}, description={self.description!r}, '
                f'test_cases={self.test_cases!r}, assertions={self.assertions!r})')


class TestCase(Base):
    __tablename__ = 'test_cases'

    id = Column(UUIDType(binary=False), primary_key=True, default=uuid.uuid4)

    input = Column(Text, nullable=False)
    expected = Column(Text, nullable=False)

    question_id = Column(UUIDType(binary=False), ForeignKey('questions.id'))

    def __repr__(self):
        return f'TestCase(id={self.id!r}, input={self.input!r}, expected={self.expected!r})'


class Assertion(Base):
    __tablename__ = 'assertions'

    id = Column(UUIDType(binary=False), primary_key=True, default=uuid.uuid4)

    assertion = Column(Text, nullable=False)
    message = Column(Text, nullable=False)

    tags = relationship("Tag", secondary=assertion_tag_relation)

    answer_id = Column(UUIDType(binary=False), ForeignKey('answers.id'))
    question_id = Column(UUIDType(binary=False), ForeignKey('questions.id'))

    def __repr__(self):
        return f'Assertion(id={self.id!r}, assertion={self.assertion!r}, message={self.message!r})'


class Tag(Base):
    __tablename__ = 'tags'

    id = Column(UUIDType(binary=False), primary_key=True, default=uuid.uuid4)

    name = Column(Text, nullable=False)
    tutorial_link = Column(Text, nullable=False)

    def __repr__(self):
        return f'Tag(id={self.id!r}, name={self.name!r}, tutorial_link={self.tutorial_link!r})'


if __name__ == '__main__':
    create_database()
