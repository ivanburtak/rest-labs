books = {
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

_counter = {"books": 4}


def next_id() -> int:
    id = _counter["books"]
    _counter["books"] += 1
    return id
