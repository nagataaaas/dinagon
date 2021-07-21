import uvicorn

from app.config import HOST, PORT

if __name__ == '__main__':
    uvicorn.run(app='app.mock:app', reload=True,
                host=HOST, port=PORT, workers=2)
