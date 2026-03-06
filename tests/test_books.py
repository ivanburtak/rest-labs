import pytest
from flask.testing import FlaskClient
from app import app
from data.books import books, _counter


@pytest.fixture(autouse=True)
def reset_db():
    books.clear()
    books.update(
        {
            1: {
                "id": 1,
                "title": "Кобзар",
                "author": "Тарас Шевченко",
                "year": 1840,
                "available": True,
            },
            2: {
                "id": 2,
                "title": "Захар Беркут",
                "author": "Іван Франко",
                "year": 1883,
                "available": True,
            },
            3: {
                "id": 3,
                "title": "Тіні забутих предків",
                "author": "Михайло Коцюбинський",
                "year": 1911,
                "available": True,
            },
        }
    )
    _counter["books"] = 4


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


# ─── GET /books ───────────────────────────────────────────────────────────────


def test_get_all_books(client: FlaskClient):
    res = client.get("/books")
    assert res.status_code == 200
    assert len(res.json) == 3


def test_get_books_filter_available(client: FlaskClient):
    books[1]["available"] = False
    res = client.get("/books?available=true")
    assert res.status_code == 200
    assert all(b["available"] for b in res.json)
    assert len(res.json) == 2


def test_get_books_filter_unavailable(client: FlaskClient):
    books[1]["available"] = False
    res = client.get("/books?available=false")
    assert res.status_code == 200
    assert len(res.json) == 1
    assert res.json[0]["id"] == 1


# ─── GET /books/<id> ──────────────────────────────────────────────────────────


def test_get_book_by_id(client: FlaskClient):
    res = client.get("/books/1")
    assert res.status_code == 200
    assert res.json["title"] == "Кобзар"


def test_get_book_not_found(client: FlaskClient):
    res = client.get("/books/999")
    assert res.status_code == 404


# ─── POST /books ──────────────────────────────────────────────────────────────


def test_create_book(client: FlaskClient):
    payload = {
        "title": "Лісова пісня",
        "author": "Леся Українка",
        "year": 1911,
    }
    res = client.post("/books", json=payload)
    assert res.status_code == 201
    assert res.json["title"] == "Лісова пісня"
    assert res.json["available"] is True
    assert res.json["id"] == 4


def test_create_book_missing_field(client: FlaskClient):
    payload = {
        "title": "Лісова пісня",
        "author": "Леся Українка",
    }  # missing year
    res = client.post("/books", json=payload)
    assert res.status_code == 400


def test_create_book_increments_id(client: FlaskClient):
    payload = {"title": "Book A", "author": "Author A", "year": 2000}
    res1 = client.post("/books", json=payload)
    res2 = client.post("/books", json=payload)
    assert res2.json["id"] == res1.json["id"] + 1


# ─── PUT /books/<id> ──────────────────────────────────────────────────────────


def test_update_book(client: FlaskClient):
    payload = {
        "title": "Кобзар (оновлено)",
        "author": "Тарас Шевченко",
        "year": 1840,
    }
    res = client.put("/books/1", json=payload)
    assert res.status_code == 200
    assert res.json["title"] == "Кобзар (оновлено)"


def test_update_book_not_found(client: FlaskClient):
    payload = {"title": "X", "author": "Y", "year": 2000}
    res = client.put("/books/999", json=payload)
    assert res.status_code == 404


def test_update_book_missing_field(client: FlaskClient):
    res = client.put("/books/1", json={"title": "Only title"})
    assert res.status_code == 400


# ─── DELETE /books/<id> ───────────────────────────────────────────────────────


def test_delete_book(client: FlaskClient):
    res = client.delete("/books/1")
    assert res.status_code == 200
    assert 1 not in books


def test_delete_book_not_found(client: FlaskClient):
    res = client.delete("/books/999")
    assert res.status_code == 404


def test_delete_removes_from_list(client: FlaskClient):
    client.delete("/books/1")
    res = client.get("/books")
    assert all(b["id"] != 1 for b in res.json)
