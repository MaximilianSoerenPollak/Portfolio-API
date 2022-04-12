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


def test_make_user_stock(authorized_client):
    stock = {}
    stock["name"] = "Teststock"
    stock["ticker"] = "TST22"
    stock["yahoo_ticker"] = "TST22"
    stock["price"] = 342.23
    res = authorized_client.post("/stocks/", json=stock)
    response = res.json()
    schemas.StockResponseSolo(**response)
    assert res.status_code == 201
    assert response["name"] == stock["name"]
    assert response["ticker"] == stock["ticker"]
    assert response["created_by"] == 1


def test_get_user_made_stock(authorized_client, test_user_stock):
    res = authorized_client.get("/stocks/TST22")
    response = res.json()
    schemas.StockResponseSolo(**response)
    assert res.status_code == 200
    assert response["name"] == "Teststock"
    assert response["price"] == 342.23


def test_update_user_stock(authorized_client, test_user_stock):
    stock = {}
    stock["name"] = "Teststock_Updated"
    stock["ticker"] = "TST22"
    stock["yahoo_ticker"] = "TST22"
    stock["price"] = 431.20
    stock["status"] = 0
    res = authorized_client.put("/stocks/TST22", json=stock)
    response = res.json()
    print(response)
    schemas.StockResponseSolo(**response)
    assert res.status_code == 200
    assert response["name"] == "Teststock_Updated"

# Test to see if we get unauthorized error.
def test_authorization_update_stock(client):
    stock = {}
    stock["name"] = "Teststock_Updated"
    stock["ticker"] = "TST22"
    stock["yahoo_ticker"] = "TST22"
    stock["price"] = 431.20
    res = client.put("/stocks/TST22", json=stock)
    assert res.status_code == 401
