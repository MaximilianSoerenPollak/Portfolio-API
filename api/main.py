import psycopg2
import time
from fastapi import FastAPI
from decouple import config
from psycopg2.extras import RealDictCursor
from .database import engine
from . import models
from .routers import stock, user, auth, portfolio

models.Base.metadata.create_all(bind=engine)


app = FastAPI()


while True:
    try:
        conn = psycopg2.connect(
            host=config("DATABASEIP"),
            database=config("DATABASENAME"),
            user=config("POSTGRESUSERNAME"),
            password=config("POSTGRESPASSWORD"),
            cursor_factory=RealDictCursor,
        )
        cursor = conn.cursor()
        print("Database connection was successful")
        break
    except Exception as e:
        print("Connecting to database failed")
        print("Error: ", e)
        time.sleep(2)


app.include_router(stock.router)
app.include_router(user.router)
app.include_router(auth.router)
app.include_router(portfolio.router)


@app.get("/")
async def root():
    return {"message": "Welcome to my API!"}
