#!/usr/bin/env python
""" Create database from ini files

    Create an sqlite3 database from the ini files in a directory.
    Invoked by ./create_db.py <db-name> <directory-path>

"""
import os
from glob import glob
import argparse
from ConfigParser import SafeConfigParser
import sqlite3

class ConstructDatabase(object):

    def __init__(self, sqlite_file):
        if os.path.exists(sqlite_file):
            open(sqlite_file, 'w').close()
        self.conn = sqlite3.connect(sqlite_file)
        self.cursor = self.conn.cursor()
        self.dir_path = None

    def process(self, dir_paths):
        self.dir_paths = dir_paths
        self.create_tables()
        self.populate_tables()
        self.conn.commit()
        self.conn.close()

    def populate_tables(self):
        files = list()
        for path in self.dir_paths:
            files.extend(glob(os.path.join(path, "*.ini")))

        for file_ in files:
            self.insert_in_db(self.extract_from_ini(file_))

    def insert_in_db(self, record):
        """ Insert database row build from dict """
        kind, dict_ = record
        fields = [x for x in dict_ if dict_[x] != ""]
        if not fields:
            self.cursor.execute("insert into %s default values" % kind)
        else:
            self.cursor.execute(
                "INSERT INTO %s (%s)" % (kind, ", ".join(fields)) +
                "VALUES (%s)" % ", ".join("?" * len(fields)),
                tuple([dict_[x] for x in fields]))

    def extract_from_ini(self, file_):
        """ Return dict of field values from ini file """
        parser = SafeConfigParser()
        parser.read(file_)
        if parser.has_section('upload'):
            combined = dict(("orig_"+x[0], x[1])
                for x in parser.items("upload"))
            combined['image_file'] = combined.pop('orig_image_file')
            combined.update(dict(parser.items("edit")))
            combined['ini_id'] = combined.pop('id')
            return 'course', combined

        elif parser.has_section('template'):
            combined = dict(parser.items('template'))
            return 'template', combined


    def create_tables(self):
        """ Create tables from schema in file tables.sql """
        with open('tables.sql', 'r') as f:
            schema = f.read()
        self.conn.executescript(schema)

def main():
    """ Commandline program to create food diary dataabase from ini files """
    parser = argparse.ArgumentParser(description="create sqlite file from ini files")
    parser.add_argument("sqlite_file", type=str, help="output database file")
    parser.add_argument("input_paths", type=str, nargs="+", help="path to ini files")
    args = parser.parse_args()
    ConstructDatabase(args.sqlite_file).process(args.input_paths)

if __name__ == '__main__':
    main()


