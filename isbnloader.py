__author__ = 'carlos'


import urllib.request
import json
import string
import re
import logging
import html.parser
import socket

DEFAULT_USER_IP = socket.gethostbyname(socket.gethostname())
IMG_WIDTH = 480
HEADER_N = 3
HTML_PARSER = html.parser.HTMLParser()
ENCODING = 'utf-8'
API_URL_GOOGLE_IMG = 'https://ajax.googleapis.com/ajax/services/search/images?v=1.0&q={}&userip={}'
API_URL_GOOGLE = 'https://ajax.googleapis.com/ajax/services/search/web?v=1.0&q={}&userip={}'
API_URL_GOOGLE_Q = 'http://www.google.com/search?q={}'


class Isbn:
    RE = re.compile(r'^(\d{13}|\d{10})$')

    def __init__(self, number):
        self.number = self.remove_punctuation(number.strip())
        if not self.RE.search(self.number):
            raise SyntaxError("Invalid format {}".format(self.number))

    @staticmethod
    def remove_punctuation(text):
        return re.sub('[%s]' % re.escape(string.punctuation), '', text)

    @staticmethod
    def load_from_file(file_path):
        with open(file_path) as f:
            isbn_set = set()
            for line in f:
                try:
                    isbn_set.add(Isbn(line))
                except SyntaxError as e:
                    logging.warning(e)
            return isbn_set

    @staticmethod
    def load_from_str(isbns_str):
        isbn_set = set()
        result = Isbn.RE.match(Isbn.remove_punctuation(isbns_str.strip()))
        if result:
            for isbn_str in result.groups():
                try:
                    isbn_set.add(Isbn(isbn_str))
                except SyntaxError as e:
                    logging.warning(e)
        return isbn_set

    @property
    def url_img(self):
        return API_URL_GOOGLE_IMG.format(self.number, DEFAULT_USER_IP)

    @property
    def url(self):
        return API_URL_GOOGLE.format(self.number, DEFAULT_USER_IP)

    @property
    def url_google_q(self):
        return API_URL_GOOGLE_Q.format(self.number)


class Book:

    HTML_FORMAT = u'<p><a href="{}">{}</a><br>ISBN:<a href="{}">{}<a/><br><img src="{}" width="{}"/></p>'

    def __init__(self, isbn, result, result_img):
        self.isbn = isbn
        self.title, self.url = self.extract_data(result['responseData']['results'])
        self.img_url = self.extract_img_url(result_img['responseData']['results'])

    @staticmethod
    def extract_img_url(result_img):
        if len(result_img) > 0:
            return result_img[0]['url']
        return None

    @staticmethod
    def extract_data(result):
        if len(result) > 0:
            return result[0]['title'], result[0]['url']
        return None, None

    def __str__(self):
        return self.title

    @property
    def html(self):
        return self.HTML_FORMAT.format(
            self.isbn.url_google_q,
            self.title,
            self.isbn.url_google_q,
            self.isbn.number,
            self.img_url,
            IMG_WIDTH,
        )

    @staticmethod
    def from_file(input_file):
        return Book.from_isbns(Isbn.load_from_file(input_file))

    @staticmethod
    def from_str(isbns):
        return Book.from_isbns(Isbn.load_from_str(isbns))

    @staticmethod
    def from_isbns(isbns):
        books = set()
        for isbn in isbns:
            request = urllib.request.Request(isbn.url, None, {'Referer': 'http://biblioln.es'})
            request_img = urllib.request.Request(isbn.url_img, None, {'Referer': 'http://biblioln.es'})
            with urllib.request.urlopen(request) as f:
                result = json.loads(f.readall().decode(ENCODING))
            with urllib.request.urlopen(request_img) as f:
                result_img = json.loads(f.readall().decode(ENCODING))
            try:
                books.add(Book(isbn, result, result_img))
            except BaseException as e:
                logging.error(e)
        return books

"""
input_file = "isbnloader_adultos.txt"
output_file = "{}.out.html".format(input_file)

with open(output_file, "w", encoding=ENCODING) as f_out:
    for book in Book.from_file(input_file):
        f_out.write(str(book))

"""