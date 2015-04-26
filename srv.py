__author__ = 'carlos'

from bottle import route, run
from isbnloader import Isbn, Book

@route('/isbn/<isbn_list>')
def from_isbn_list(isbn_list=""):
    for book in Book.from_str(isbn_list):
        return book.html


run(host='localhost', port=8080, debug=True)