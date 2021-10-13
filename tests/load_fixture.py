from app.models import *
from app.utils import hash_password


def load():
    password1, salt1 = hash_password('test1')
    user1 = User(email_address='test1@test.com', password_hash=password1, salt=salt1)

    password2, salt2 = hash_password('test2')
    user2 = User(email_address='test2@test.com', password_hash=password2, salt=salt2)

    testcase1 = [
        TestCase(id=None, input='add(0, 0)', expected='0'),
        TestCase(id=None, input='add(1, 1)', expected='2'),
        TestCase(id=None, input='add(1.0, 1.0)', expected='2.0'),
        TestCase(id=None, input='add(-1, 1)', expected='0'),
        TestCase(id=None, input='add(-2, 1)', expected='-1')
    ]
    assertions1 = [
        Assertion(assertion="'+' in code", message="加算が行われていない可能性があります"),
        Assertion(assertion="add(0, 0) === undefined", message="値が返却されていない可能性があります")
    ]

    testcase2 = [
        TestCase(id=None, input='add(0, 0, 0)', expected='0'),
        TestCase(id=None, input='add(1, 1, 1)', expected='3'),
        TestCase(id=None, input='add(1.0, 1.0, 0.5)', expected='2.5'),
        TestCase(id=None, input='add(-1, 1, 0)', expected='0'),
        TestCase(id=None, input='add(-2, 1, -1)', expected='-2')
    ]
    assertions2 = [
        Assertion(assertion="'+' in code", message="加算が行われていない可能性があります"),
        Assertion(assertion="add(0, 0) === undefined", message="値が返却されていない可能性があります")
    ]

    question1 = Question(title='add 2 values',
                         description='2つの値が与えられると、それらの値を足し合わせた数字を返す関数 `add` を定義してください。',
                         test_cases=testcase1, assertions=assertions1)
    question2 = Question(title='add 3 values',
                         description='3つの値が与えられると、それらの値を足し合わせた数字を返す関数 `add` を定義してください。',
                         test_cases=testcase2, assertions=assertions2)

    session = SessionLocal()

    session.add_all([user1, user2, *testcase1, *testcase2, *assertions1, *assertions2,
                     question1, question2])
    session.commit()

    answers = [
        Answer(user=user1.id, question=question1.id, is_correct=False),
        Answer(user=user1.id, question=question1.id, is_correct=True),
        Answer(user=user1.id, question=question2.id, is_correct=True),
        Answer(user=user2.id, question=question1.id, is_correct=True),
        Answer(user=user2.id, question=question2.id, is_correct=False),
        Answer(user=user2.id, question=question2.id, is_correct=True),
    ]

    session.add_all(answers)
    session.commit()
    session.close()


if __name__ == '__main__':
    create_database()
    load()
