# Dinagon

Backend of [Chunagon](https://github.com/nagataaaas/chunagon)

# versions

| program | version |
|---------|---------|
| Python | 3.9 |
| fastapi | 0.66.0 |
|PyJWT|2.1.0|
|SQLAlchemy|1.4.21|
|SQLAlchemy-Utils|0.37.8|

# how to run

1. Install Python3.9 from [here](https://www.python.org/downloads/). Make sure you added Python to path.
2. Install git and run `https://github.com/nagataaaas/dinagon.git`. Or simply download [zip file](https://github.com/nagataaaas/dinagon/archive/refs/heads/main.zip) and extract.
3. Move to `/dinagon`
4. Run `pip install -r requirements.txt` (or `pip3 install ...` on linux or mac).
5. Add environment variables below
    ```
    MAIL_SERVER:  'smtp.example_email_server.com'
    MAIL_PORT:     465
    MAIL_ADDRESS: 'example@example.com'
    MAIL_PASS:    'password@0123'
    JWT_SECRET:   'JWT_SECRET_KEY'
    ```
6. Edit '/dinagon/app/config.py'
7. move to `/dinagon`, and then, run `python run.py` (or `python3 run.py` as above).
8. You can see API swagger `http://{config.HOST}:{config.PORT}/docs`