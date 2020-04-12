import json
from dataclasses import dataclass
from typing import List

@dataclass
class Metadata:
    """
    Metadata for a given work.

    Attributes:
        author_sort: String to be used when sorting by author.
        authors: Set the authors. Multiple authors should be separated by ampersands.
        book_producer: Set the book producer.
        comments: Set the e-book description.
        isbn: Set the ISBN of the book.
        language: Set the language.
        pubdate: Set the publication date (assumed to be in the local timezone, unless the timezone is explicitly specified)
        publisher: Set the e-book publisher.
        rating: Set the rating. Should be a number between 1 and 5.
        series: Set the series this e-book belongs to.
        series_index: Set the index of the book in this series.
        tags: Set the tags for the book. Should be a comma separated list.
        title: Set the title.
        title_sort: The version of the title to be used for sorting.
        chapters: List of chapters to include in sorted order.
    """
    author_sort: str=None
    authors: str=None
    book_producer: str=None
    comments: str=None
    isbn: str=None
    language: str=None
    pubdate: str=None
    publisher: str=None
    rating: str=None
    series: str=None
    series_index: str=None
    tags: str=None
    title: str=None
    title_sort: str=None
    chapters: List[str]=None

    def to_json(self):
        return json.dumps({k: v for k, v in self.__dict__.items() if v}, indent=4)
