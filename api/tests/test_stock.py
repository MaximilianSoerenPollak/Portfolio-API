import datetime
from typing import List
from api import schemas


def test_get_stocks(test_stocks, authorized_client):
    res = authorized_client.get("/stocks/")
    response = res.json()
    schemas.StockResponseSolo(**(response[0]))
    assert len(response) == 10
    assert type(response[3]["name"]) == str


def test_get_all_stocks(test_stocks, authorized_client):
    res = authorized_client.get("/stocks/?all_stocks=True")
    response = res.json()
    schemas.StockResponseSolo(**(response[0]))
    assert len(response) == len(test_stocks)
