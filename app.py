from flask import Flask
from flask_restful import Api
from flasgger import Swagger

from models.books import BOOK_SCHEMA
from resources.books import BookListResource, BookResource

app = Flask(__name__)
api = Api(app)

swagger_template = {
    "swagger": "2.0",
    "info": {
        "title": "Library API",
        "description": "REST API для управління бібліотекою книг.",
        "version": "1.0.0",
    },
    "basePath": "/",
    "schemes": ["http"],
    "tags": [
        {"name": "Books", "description": "CRUD операції з книгами"},
    ],
    "definitions": BOOK_SCHEMA,
}

Swagger(app, template=swagger_template)

api.add_resource(BookListResource, "/books")
api.add_resource(BookResource, "/books/<int:book_id>")

if __name__ == "__main__":
    app.run(debug=True, port=5000)
