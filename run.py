import uvicorn

from app.config import HOST, PORT, IS_MOCK, IS_DEV
from app.models import create_database, clear_database
from testing.load_fixture import load

from sqlalchemy.exc import IntegrityError

if __name__ == '__main__':
    # clear_database()
    # create_database()
    # if IS_DEV:
    #     try:
    #         load()
    #     except IntegrityError:
    #         pass
    if IS_MOCK:
        uvicorn.run(app='test.mock:app', reload=True, host=HOST, port=PORT, workers=2)
    else:
        uvicorn.run(app='app.routes:app', reload=True, host=HOST, port=PORT, workers=2)
