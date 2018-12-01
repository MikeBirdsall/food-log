#!/usr/bin/python3

# Stub code

from collections import namedtuple, defaultdict
import sqlite3
from datetime import date
from operator import attrgetter


RAW_ITEM = namedtuple('raw_item', 'id comment carbs description calories fat '
    'day time protein size ini_id thumb_id')

ANON_ITEM = namedtuple('anon_item', 'comment carbs description calories fat '
    'protein size')

class Assessed:
    def __init__(self):
        self.canonical = None
        self.count = 0
        self.ids = set()
        self.first_day = date.max
        self.last_day = date.min
        self.score = 0

    def update(self, candidate):
        self.count += 1
        self.ids.add(candidate.id)
        self.first_day = min(self.first_day, candidate.day)
        self.canonical = candidate
        self.assess()

    def assess(self):
        self.score += self.count
        if self.canonical.calories:
            self.score += 20
        for attr in 'fat protein carbs'.split():
            if getattr(self.canonical, attr):
                self.score += 3




class TextSearchEngine:

    def __init__(self, DB_FILE, searchstring):
        self.searchstring = searchstring
        self.assessed_courses = defaultdict(Assessed)

        with sqlite3.connect(
                DB_FILE,
                detect_types=sqlite3.PARSE_DECLTYPES) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            sql = """select id, comment, carbs, description, calories,
                fat, day, time, protein, size, ini_id, thumb_id
                from course
                where id in (
                    select course_id from fulltext where content match ?)
            """
            cursor.execute(sql, (searchstring,))

            for course in cursor.fetchall():
                ritem = RAW_ITEM(**{
                    k: v for k, v in dict(course).items()
                    if k in RAW_ITEM._fields}
                )
                aitem = str(ANON_ITEM(**{
                    k: v for k, v in dict(course).items()
                    if k in ANON_ITEM._fields}
                )).lower()
                self.assessed_courses[aitem].update(ritem)


    def results(self):
        """ Filter and Rank the results

            Create one "canonical" entry for duplicates apart from id,
            Rank them to prefer:
               those with calories filled out,
               those with more nutrients filled out,
               those that are neither too new (1 week) or too old (> 1 year)
       """

        answer = sorted(
            self.assessed_courses.values(),
            key=attrgetter('score'),
            reverse=True,
        )
        answer = [(x.canonical, x.score) for x in answer]
        return answer

