import uvicorn

from app.config import HOST, PORT, IS_MOCK

if __name__ == '__main__':
    if IS_MOCK:
        uvicorn.run(app='test.mock:app', reload=True, host=HOST, port=PORT, workers=2)
    else:
        uvicorn.run(app='app.routes:app', reload=True, host=HOST, port=PORT, workers=2)
