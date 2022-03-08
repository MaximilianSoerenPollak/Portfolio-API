from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine
from . import models
from .routers import stock, user, auth, portfolio

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(stock.router)
app.include_router(user.router)
app.include_router(auth.router)
app.include_router(portfolio.router)


@app.get("/")
async def root():
    return {"message": "Welcome to my API!"}
