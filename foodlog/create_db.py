#!/usr/bin/env python3
""" Create database from ini files

    I started out using ini files as the first input and primary backup method
    for the data. I'm changing that to be more database centric, with the
    backup being done by a file containing a log of the sql statements used to
    update the database. This version will create the database, but also save
    a copy of the sql used to create it.

"""
import os
import argparse
import sqlite3
from foodlog.my_info import config_path

class ConstructDatabase:

    def __init__(self, args):
        config = config_path()
        sqlite_file = args.sqlite_file or config.dir("DB_FILE")
        log_file = args.log_file or config.dir("DB_LOG")

        if os.path.exists(sqlite_file):
            open(sqlite_file, 'w').close()
        self.conn = sqlite3.connect(sqlite_file)
        self.cursor = self.conn.cursor()
        self.log_file = open(log_file, 'w')

    def process(self):
        self.create_tables()
        self.conn.commit()
        self.conn.close()

    def create_tables(self):
        """ Create tables from schema in file tables.sql """
        with open('tables.sql', 'r') as sqlite_file:
            schema = sqlite_file.read()
        self.conn.executescript(schema)
        print(schema, file=self.log_file)

def main():
    """ Commandline program to create food diary database from ini files """
    parser = argparse.ArgumentParser(description="create sqlite file from ini files")
    parser.add_argument("input_paths", type=str, nargs="*", help="path to ini files")
    parser.add_argument("--sqlite_file", '-d', type=str, help="output database file")
    parser.add_argument("--log_file", '-l', type=str, help="output sql log file")
    args = parser.parse_args()
    ConstructDatabase(args).process()

if __name__ == '__main__':
    main()


