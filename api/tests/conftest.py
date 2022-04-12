import pytest
import string
import random
import api.models as models
from fastapi.testclient import TestClient
from api.main import app
from api.config import settings
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from api.database import get_db, Base
from api.oauth2 import create_access_token


# ---- SETUP FOR DB -----
SQLALCHEMY_DATABASE_URL = f"postgresql://{settings.POSTGRES_USERNAME}:{settings.POSTGRES_PASSWORD}@{settings.DATABASE_HOSTNAME}:{settings.DATABASE_PORT}/{settings.DATABASE_NAME}_test"

engine = create_engine(SQLALCHEMY_DATABASE_URL)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


# ---- TESTS ----
@pytest.fixture()
def session(scope="session"):
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture()
def client(session, scope="session"):
    def override_get_db():
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)


@pytest.fixture
def test_user(client):
    user_data = {"email": "testcreate@example.com", "password": "password123"}
    res = client.post("/users/", json=user_data)
    assert res.status_code == 201
    new_user = res.json()
    new_user["password"] = user_data["password"]
    return new_user


@pytest.fixture
def token(test_user):
    return create_access_token({"user_id": test_user["id"]})


@pytest.fixture
def authorized_client(client, token):
    client.headers = {**client.headers, "Authorization": f"Bearer {token}"}
    return client


# ----- Inserting Stocks -----

RECORD_NUMBER = 1000


@pytest.fixture
def test_stocks(session):
    stock_list = []
    names = []
    tickers = []
    prices = []
    for _ in range(RECORD_NUMBER):
        names.append(
            "".join(random.choices(string.ascii_letters, k=random.randrange(5, 20)))
        )
        tickers.append(
            "".join(random.choices(string.ascii_uppercase, k=random.randrange(5)))
        )
        prices.append(round(random.uniform(0.5, 4000), 2))
    tickers = set(tickers)
    tickers = list(tickers)
    names = names[: len(tickers)]
    prices = prices[: len(tickers)]
    for i in range(len(tickers)):
        stock_dict = {}
        stock_dict["name"] = names[i]
        stock_dict["ticker"] = tickers[i]
        stock_dict["yahoo_ticker"] = tickers[i]
        stock_dict["price"] = prices[i]
        stock_list.append(stock_dict)

    def create_stock(stock):
        return models.Stock(**stock)

    stock_map = map(create_stock, stock_list)
    stocks = list(stock_map)
    session.add_all(stocks)
    session.commit()
    stocks = session.query(models.Stock).all()
    return stocks

# Make a permanent Test stock that a user can update / delete
@pytest.fixture
def test_user_stock(session):
    stock = {}
    stock["name"] = "Teststock"
    stock["ticker"] = "TST22"
    stock["yahoo_ticker"] = "TST22"
    stock["price"] = 342.23
    stock["created_by"] = 1
    stock_model = models.Stock(**stock)
    session.add(stock_model)
    session.commit()
    stock_indb = (
        session.query(models.Stock).filter(models.Stock.created_by == 1).first()
    )
    return stock_indb
