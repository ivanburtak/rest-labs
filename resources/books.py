from flask import request
from flask_restful import Resource, reqparse, abort
from data.books import books, next_id


book_parser = reqparse.RequestParser()
book_parser.add_argument("title", type=str, required=True, help="title is required")
book_parser.add_argument("author", type=str, required=True, help="author is required")
book_parser.add_argument("year", type=int, required=True, help="year is required")


def get_or_404(book_id: int) -> dict:
    book = books.get(book_id)
    if not book:
        abort(404, message=f"Book {book_id} not found")
    return book


class BookListResource(Resource):
    def get(self):
        """
        Get all books
        ---
        tags:
          - Books
        parameters:
          - name: available
            in: query
            type: boolean
            required: false
            description: Filter by availability
        responses:
          200:
            description: List of books
            schema:
              type: array
              items:
                $ref: '#/definitions/Book'
        """
        available = request.args.get("available")
        result = list(books.values())
        if available is not None:
            flag = available.lower() == "true"
            result = [b for b in result if b["available"] == flag]
        return result, 200

    def post(self):
        """
        Add a new book
        ---
        tags:
          - Books
        parameters:
          - in: body
            name: body
            required: true
            schema:
              $ref: '#/definitions/Book'
        responses:
          201:
            description: Book created
            schema:
              $ref: '#/definitions/Book'
          400:
            description: Validation error
        """
        args = book_parser.parse_args()
        book = {"id": next_id(), "available": True, **args}
        books[book["id"]] = book
        return book, 201


class BookResource(Resource):
    def get(self, book_id: int):
        """
        Get a book by ID
        ---
        tags:
          - Books
        parameters:
          - name: book_id
            in: path
            type: integer
            required: true
        responses:
          200:
            description: Book data
            schema:
              $ref: '#/definitions/Book'
          404:
            description: Book not found
        """
        return get_or_404(book_id), 200

    def put(self, book_id: int):
        """
        Update a book by ID
        ---
        tags:
          - Books
        parameters:
          - name: book_id
            in: path
            type: integer
            required: true
          - in: body
            name: body
            required: true
            schema:
              $ref: '#/definitions/Book'
        responses:
          200:
            description: Updated book
            schema:
              $ref: '#/definitions/Book'
          404:
            description: Book not found
        """
        book = get_or_404(book_id)
        args = book_parser.parse_args()
        book.update(args)
        return book, 200

    def delete(self, book_id):
        """
        Delete a book by ID
        ---
        tags:
          - Books
        parameters:
          - name: book_id
            in: path
            type: integer
            required: true
        responses:
          200:
            description: Book deleted
          404:
            description: Book not found
        """
        get_or_404(book_id)
        del books[book_id]
        return {"message": f"Book {book_id} deleted"}, 200
