from typing import List
from api import schemas


def test_get_stocks(authorized_client):
    res = authorized_client.get("/stocks?limit=1/")
    response = schemas.StockResponseSolo(res.json())
    assert len(response) == 1


def test_get_stocks_default_limit(authorized_client):
    res = authorized_client.get("/stocks/")
    assert type(res.json()) == list
    assert len(res.json()) == 10
# def test_get_all_stocks_user(authorized_client)
 