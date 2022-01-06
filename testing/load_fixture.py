from app.models import *
import glob
import json


def load():
    session = SessionLocal()

    tags = [
        Tag(name='変数', tutorial_link='https://developer.mozilla.org/ja/docs/Learn/JavaScript/First_steps/Variables'),
        Tag(name='if文',
            tutorial_link='https://developer.mozilla.org/ja/docs/Web/JavaScript/Guide/Control_flow_and_error_handling#conditional_statements'),
        Tag(name='算術理解', tutorial_link='https://developer.mozilla.org/ja/docs/Learn/JavaScript/First_steps/Math'),
        Tag(name='関数定義', tutorial_link='https://developer.mozilla.org/ja/docs/Web/JavaScript/Guide/Functions'),
        Tag(name='関数呼び出し',
            tutorial_link='https://developer.mozilla.org/ja/docs/Web/JavaScript/Guide/Functions#calling_functions'),
        Tag(name='定数', tutorial_link='https://developer.mozilla.org/ja/docs/Web/JavaScript/Reference/Statements/const'),
        Tag(name='関数からの値の返却',
            tutorial_link='https://developer.mozilla.org/ja/docs/Web/JavaScript/Reference/Statements/return'),
        Tag(name='for文',
            tutorial_link='https://developer.mozilla.org/ja/docs/Web/JavaScript/Guide/Loops_and_iteration#for_statement'),
        Tag(name='型理解',
            tutorial_link='https://developer.mozilla.org/ja/docs/Web/JavaScript/Guide/Grammar_and_Types#data_structures_and_types')]

    session.add_all(tags)
    session.commit()
    tag_dict = {tag.name: tag for tag in tags}

    for file in glob.glob('./shonagon/assertions/*'):
        with open(file, 'r', encoding='utf-8') as f:
            data = json.loads(f.read())

        testcases = [TestCase(**case) for case in data['testCase']]
        assertions = [Assertion(assertion=json.dumps(assertion['assertion']),
                                message=assertion['message'],
                                tags=[tag_dict[tag] for tag in assertion['tags']])
                      for assertion in data['assertions']]

        question = Question(title=data['title'], description=data['description'],
                            test_cases=testcases, assertions=assertions, tags=[tag_dict[tag] for tag in data['tags']],
                            default_code=data['defaultCode'])

        session.add_all([*testcases, *assertions, question])

    session.commit()
    session.close()


if __name__ == '__main__':
    create_database()
    load()
