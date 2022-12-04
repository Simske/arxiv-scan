"""Definition of class Entry and all evaluation related functions"""
import re
from datetime import datetime
from typing import Dict, List, Optional


class Entry(object):
    """This class represents one arxiv entry"""

    def __init__(self, id: str, title: str,
                 authors: List[str], abstract: str,
                 date_submitted: datetime,
                 date_updated: datetime,
                 category: str = "",
                 number: Optional[int] = None) -> None:
        self.id = id
        self.title = title
        self.authors = authors
        self.abstract = abstract
        self.category = category
        self.date_submitted = date_submitted
        self.date_updated = date_updated

        self.title_marks: List[int] = []
        self.author_marks: List[bool] = [False] * len(self.authors)
        self.rating: int = -1 # -1 if rating is not calculated

    def __repr__(self) -> str:
        return (
            f"{type(self).__name__}(\n    id={self.id!r},\n    title={self.title!r},\n    "
            f"authors={self.authors!r},\n    abstract={self.abstract!r},\n    "
            f"category={self.category!r},\n    "
            f"date_submitted={self.date_submitted!r},\n    date_updated={self.date_updated!r}"
            "\n)"
        )

    def mark_title_position(self, position: int) -> None:
        """Mark title at given position"""
        self.title_marks.append(position)

    def mark_title_keyword(self, keyword: str) -> None:
        """Mark title at positions where keyword is found"""
        counts = self.title.lower().count(keyword)
        for _ in range(counts):
            starts = [m.start() for m in re.finditer(keyword, self.title.lower())]
            ends = [m.end() for m in re.finditer(keyword, self.title.lower())]
            for s, e in zip(starts, ends):
                for pos in range(s, e):
                    self.mark_title_position(pos)

    def mark_author(self, number: int) -> None:
        """Mark author (by given number in author list)"""
        self.author_marks[number] = True

    def evaluate(self, keyword_ratings: Dict[str, int], author_ratings: Dict[str, int],
                       rate_abstract: bool=True) -> int:
        """Evaluate entry

        Rate entries according to keywords and author list.
        This sets the rating attribute and marks title and marks title words and authors.

        Args:
            keywords (dict): dict with keywords as keys and rating as value
            authors (dict): dict with authors as keys and rating as value
        Returns:
            int: rating for this entry
        """
        self.rating = 0
        # find keywords in title and abstract
        for keyword, rating in keyword_ratings.items():
            keyword = keyword.lower()
            # find and mark keyword in title
            counts = self.title.lower().count(keyword)
            if counts > 0:
                self.mark_title_keyword(keyword)
                self.rating += counts * rating
            # find keyword in abstract
            if rate_abstract:
                self.rating += self.abstract.lower().count(keyword) * rating

        # find authors
        for author, rating in author_ratings.items():
            for i, a in enumerate(self.authors):
                match = re.search(r'\b{}\b'.format(author), a, flags=re.IGNORECASE)
                if match:
                    self.mark_author(i)
                    self.rating += rating

        return self.rating

def evaluate_entries(entries: List[Entry], keyword_ratings: Dict[str, int],
                     author_ratings: Dict[str, int], rate_abstract: bool=True) -> List[Entry]:
    """Evaluate all entries in list"""
    for entry in entries:
        entry.evaluate(keyword_ratings, author_ratings, rate_abstract)
    return entries

def sort_entries(entries: List[Entry], rating_min: int, reverse: bool,
                 length: Optional[int]=None) -> List[Entry]:
    ''' Sort entries by rating

    Only entries with rating >= rating_min are listed, and the list is at
    maximum length entries long. If reverse is True, the entries are reversed
    (after cutting the list to length entries). Note that the default order
    is most relevant paper on top.
    '''
    if length is not None and length < 0:
        length = None

    # remove entries with low rating
    entries_filtered = filter(lambda entry: entry.rating >= rating_min, entries)
    # sort by rating
    results = sorted(entries_filtered, key=lambda x: x.rating, reverse=not reverse)

    return results[:length]
