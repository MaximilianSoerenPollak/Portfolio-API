from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from .database import engine
from . import models
import logging
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from .routers import stock, user, auth, portfolio

app = FastAPI(debug=True)

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
    return {"message": "Welcome to my API!"}


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    exc_str = f"{exc}".replace("\n", " ").replace("   ", " ")
    logging.error(f"{request}: {exc_str}")
    content = {"status_code": 10422, "message": exc_str, "data": None}
    return JSONResponse(content=content, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)
