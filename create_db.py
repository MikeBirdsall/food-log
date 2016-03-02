#!/usr/bin/env python
""" Create database from ini files

    I started out using ini files as the first input and primary backup method
    for the data. I'm changing that to be more database centric, with the
    backup being done by a file containing a log of the sql statements used to
    update the database. This version will create the database, but also save
    a copy of the sql used to create it.

"""
import os
from glob import glob
import argparse
from ConfigParser import SafeConfigParser
import sqlite3
from my_info import config_path

class ConstructDatabase(object):

    def __init__(self, args):
        config = config_path()
        sqlite_file = args.sqlite_file or config.dir("DB_FILE")
        log_file = args.log_file or config.dir("DB_LOG")
        self.default_ini_files = list((config.dir("DATA_DIR"), config.dir("TEMPLATE_DIR")))

        if os.path.exists(sqlite_file):
            open(sqlite_file, 'w').close()
        self.conn = sqlite3.connect(sqlite_file)
        self.cursor = self.conn.cursor()
        self.log_file = open(log_file, 'w')
        self.dir_paths = None

    def process(self, dir_paths):
        self.dir_paths = dir_paths or self.default_ini_files
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
        if fields:
            vals = [dict_[x] for x in fields]
            line = "INSERT INTO %s (%s) VALUES(%s)" % (
                kind, ", ".join(fields), ", ".join("?" for x in fields))
            self.cursor.execute(line, parms)
            print >> self.log_file, dict(command=line, args=parms)
        else:
            raise RuntimeError('no fields in record: %s', dict_)

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
        print >> self.log_file, schema

def main():
    """ Commandline program to create food diary database from ini files """
    parser = argparse.ArgumentParser(description="create sqlite file from ini files")
    parser.add_argument("input_paths", type=str, nargs="*", help="path to ini files")
    parser.add_argument("--sqlite_file", '-d', type=str, help="output database file")
    parser.add_argument("--log_file", '-l', type=str, help="output sql log file")
    args = parser.parse_args()
    ConstructDatabase(args).process(args.input_paths)

if __name__ == '__main__':
    main()


