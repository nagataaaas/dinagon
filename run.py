import uvicorn

from app.config import HOST, PORT, IS_DEV
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
    uvicorn.run(app='app.routes:app', reload=True, host=HOST, port=PORT, workers=2)
