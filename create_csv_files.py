#!/usr/bin/env python
# encoding: utf-8
"""
Create a number of fake CVS files. These files have an arbitrary length (from 5 lines to 1000),
and each have 7 columns. Requires the module Faker (http://faker.readthedocs.io/en/master/).
This script was based on the Ryan Wilcox code (https://gist.github.com/rwilcox/455453).
Please consider this code as part of the public domain

Rodrigo Estevao
"""

import os
import errno

from re import sub
from zipfile import ZipFile
from sys import argv
from csv import DictWriter
from random import randrange
from faker import Faker
from shutil import copyfileobj, rmtree

class CsvGenerator:

    def __init__(
        self,
        num_of_files=1,
        num_of_buckets=0,
        destination_path='.',
        compress=False,
        delimiter=','
    ):
        self.__bucket_list = []
        self.__file_list = []
        self.__fake = Faker()

        self.num_of_files = max(1, int(num_of_files))
        self.num_of_buckets = min(int(num_of_buckets), self.num_of_files)
        self.destination_path = str(destination_path).strip(os.sep).strip() + os.sep
        self.compress = compress
        self.delimiter = delimiter

    def __str__(self):
        result = "{"
        result += "num_of_files: " + str(self.num_of_files) + ", "
        result += "num_of_buckets: " + str(self.num_of_buckets) + ", "
        result += "destination_path: " + self.destination_path + ", "
        result += "compress: " + str(self.compress) + ", "
        result += "delimiter: " + self.delimiter
        result += "}"
        return result

    @staticmethod
    def __random_enumerator(start=5, stop=1001):
        enumerator = randrange(start, stop)
        for row in range(start, enumerator):
            yield row

    @staticmethod
    def __create_dirs(dirs):
        if dirs and not os.path.exists(dirs):
            try:
                os.makedirs(dirs)
            except OSError as e:
                if e.errno != errno.EEXIST:
                    raise
        return os.path.isdir(dirs)

    @staticmethod
    def __compress_file(file_path):
        result = False
        if os.path.isfile(file_path):
            zip_file_path = sub('(?i)\.\w+$', '.zip', file_path.strip())
            with ZipFile(zip_file_path, 'w') as zip_file:
                zip_file.write(file_path)
            result = os.path.isfile(zip_file_path)
        return result

    @staticmethod
    def __compress_dir(dir_path):
        result = False
        if os.path.isdir(dir_path):
            path = os.path.abspath(dir_path)
            zip_name = path + '.zip'

            with ZipFile(zip_name, 'w') as zip_file:
                for root, subdirs, files in os.walk(dir_path):
                    dest_dir = os.path.basename(root)
                    for file in files:
                        zip_file.write(os.path.join(root, file), arcname=os.path.join(dest_dir, file))
            result = os.path.isfile(zip_name)
        return result

    def __create_bucket_list(self):
        self.__bucket_list = []
        if self.num_of_buckets > 0:
            for index in range(self.num_of_buckets):
                bucket_path = os.path.join(self.destination_path, 'B{:03}'.format(index + 1))

                if os.path.isdir(bucket_path):
                    rmtree(path=bucket_path)

                self.__bucket_list.append(bucket_path)
        else:
            self.__bucket_list.append(self.destination_path)

        return (self.num_of_buckets == 0) or (len(self.__bucket_list) == self.num_of_buckets)

    def __create_csv_file(self, file_path):
        result = False
        if file_path:
            file_dir = os.path.dirname(file_path)

            if not os.path.isdir(file_dir):
                CsvGenerator.__create_dirs(file_dir)

            with open(file_path, "w", newline='') as csv_file:
                writer = DictWriter(csv_file, delimiter=self.delimiter, fieldnames=["name", "phone", "address", "city", "state", "zip", "notes"])
                writer.writeheader()
                for _ in CsvGenerator.__random_enumerator():
                    writer.writerow({
                        'name': self.__fake.name(),
                        'phone': self.__fake.phone_number(),
                        'address': self.__fake.street_address(),
                        'city': self.__fake.city(),
                        'state': self.__fake.state_abbr(),
                        'zip': self.__fake.zipcode(),
                        'notes': self.__fake.text(),
                    })

            result = os.path.isfile(file_path)

            if result:
                self.__file_list.append(file_path)

        return result

    def generate(self):
        self.__create_bucket_list()
        for bucket in self.__bucket_list:
            for index in range(self.num_of_files):
                file_path = os.path.join(bucket, 'F{:03}.csv'.format(index + 1))
                if self.__create_csv_file(file_path=file_path) and self.compress:
                    if self.num_of_buckets == 0:
                        CsvGenerator.__compress_file(file_path=file_path)
                        os.remove(file_path)

            if self.compress and self.num_of_buckets > 0:
                CsvGenerator.__compress_dir(dir_path=bucket)


from argparse import ArgumentParser

if __name__ == '__main__':

    def str2bool(value):
        result = False
        if value.lower().strip() in ('yes', 'true', 't', 'y', '1'):
            result = True
        elif value.lower().strip() in ('no', 'false', 'f', 'n', '0'):
            result = False
        else:
            raise argparse.ArgumentTypeError('Boolean value expected.')
        return result


    parser = ArgumentParser(description='Generate random files with some random content')
    parser.add_argument('-n', '--num_of_files', metavar='N', type=int, default=1, help='Number of files to be generated')
    parser.add_argument('-b', '--num_of_buckets', metavar='N', type=int, default=0, help='Number of buckets (extra dir) that are going to be created. If specified, each bucket will have a random number of files from 1 to the value specified on --files.')
    parser.add_argument('-p', '--destination_path', default='.', help='Destination directory')
    parser.add_argument('-d', '--delimiter', type=str, default=',', help='Delimiter used to separate the records on files')
    parser.add_argument('-c', '--compress', metavar='BOOL', type=str2bool, nargs='?', const=True, default=False, help='Defines if the random files or buckets shall be compressed or not.')
    args = parser.parse_args()

    generator = CsvGenerator(
        num_of_files=args.num_of_files,
        num_of_buckets=args.num_of_buckets,
        destination_path=args.destination_path,
        delimiter=args.delimiter,
        compress=args.compress
    )

    generator.generate()
