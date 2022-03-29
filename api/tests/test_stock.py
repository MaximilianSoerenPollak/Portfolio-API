from typing import List
from api import schemas


def test_get_stocks(authorized_client):
    res = authorized_client.get("/stocks/")
    print(res.content)
    response = List[schemas.StockResponseSolo()]
    assert len(response) == 10


# def test_get_all_stocks_user(authorized_client)
