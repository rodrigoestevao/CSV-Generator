#!/usr/bin/env python
# encoding: utf-8
"""
Create a number of fake CVS files. These files have an arbitrary length (from 5 lines to 1000),
and each have 7 columns. Requires the module Faker (http://faker.readthedocs.io/en/master/).
This script was based on the Ryan Wilcox code (https://gist.github.com/rwilcox/455453).
Please consider this code as part of the public domain

Rodrigo Estevao
"""

import os, errno, gzip

from sys import argv
from csv import DictWriter
from random import randrange
from faker import Faker
from shutil import copyfileobj

class CsvGenerator:

    def __init__(self, files, path, compress):
        self.files = max(1, int(files))
        self.path = str(path).strip(os.sep).strip() + os.sep
        self.compress = compress

    @staticmethod
    def random_enumerator():
        enumerator = randrange(5, 1001)
        for row in range(5, enumerator):
            yield row


    def create_destination_path_if_needed(self):
        if not os.path.exists(self.path):
            try:
                os.makedirs(self.path)
            except OSError as e:
                if e.errno != errno.EEXIST:
                    raise


    def generate(self):
        self.create_destination_path_if_needed()

        fake = Faker()

        for index in range(self.files):
            file_name = self.path + "{:03}.csv".format(index + 1)
            with open(file_name, "w", newline='') as csv_file:
                writer = DictWriter(csv_file, delimiter=';', fieldnames=["name", "phone", "address", "city", "state", "zip", "notes"])
                writer.writeheader()
                for _ in self.random_enumerator():
                    writer.writerow({
                        'name': fake.name(),
                        'phone': fake.phone_number(),
                        'address': fake.street_address(),
                        'city': fake.city(),
                        'state': fake.state_abbr(),
                        'zip': fake.zipcode(),
                        'notes': fake.text(),
                    })

            if self.compress:
                with open(file_name, 'rb') as csv_file:
                    with gzip.open("{}.gz".format(file_name), 'wb') as gz_file:
                        copyfileobj(csv_file, gz_file)
                os.remove(file_name)

import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate random files with some random content')
    parser.add_argument('-f', '--files', metavar='N', type=int, default=1, help='Number of files to be generated')
    parser.add_argument('-p', '--path', default='.', help='Destination directory')
    parser.add_argument('-c', '--compress', type=bool, default=False, help='If true, the generated files will be compressed as .gz file, if false they will be generated as .csv without compression.')
    args = parser.parse_args()

    generator = CsvGenerator(
        files=args.files,
        path=args.path,
        compress=args.compress
    )
    generator.generate()
