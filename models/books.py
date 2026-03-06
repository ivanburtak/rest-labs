BOOK_SCHEMA = {
    "Book": {
        "type": "object",
        "properties": {
            "id": {"type": "integer", "example": 1},
            "title": {"type": "string", "example": "Кобзар"},
            "author": {"type": "string", "example": "Тарас Шевченко"},
            "year": {"type": "integer", "example": 1840},
            "available": {"type": "boolean", "example": True},
            "description": {
                "type": "string",
                "example": "У віршах збірки йдеться про свободу, несправедливість у суспільстві, життя й боротьбу українського народу, а також любов до рідної землі.",
            },
        },
        "required": ["title", "author", "year"],
    }
}
