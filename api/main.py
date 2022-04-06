import logging
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from api.database import engine
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from api.routers import stock, user, auth, portfolio

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
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
    return {"message": "Hello, this is my API!"}
