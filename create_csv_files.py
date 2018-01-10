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
from shutil import copyfileobj

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

        self.fake = Faker()
        self.num_of_files = max(1, int(num_of_files))
        self.num_of_buckets = min(int(num_of_buckets), self.num_of_files)
        self.destination_path = str(destination_path).strip(os.sep).strip() + os.sep
        self.compress = compress
        self.delimiter = delimiter

    def __str__(self):
        result = "{"
        result += "__bucket_list: " + str(self.__bucket_list).strip() + ", "
        result += "__file_list: " + str(self.__file_list).strip() + ", "
        result += "num_of_files: " + str(self.num_of_files).strip() + ", "
        result += "num_of_buckets: " + str(self.num_of_buckets).strip() + ", "
        result += "destination_path: " + self.destination_path.strip() + ", "
        result += "compress: " + str(self.compress).strip() + ", "
        result += "delimiter: " + str(self.delimiter).strip()
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
            zip_file_path = dir_path.strip() + '.zip'
            with ZipFile(zip_file_path, 'w') as zip_file:
                for dirname, subdirs, files in os.walk(dir_path):
                    zip_file.wirte(dirname)
                    for filename in files:
                        zip_file(os.path.join(dirname, filename))
            result = os.path.isfile(zip_file_path)

        return result


    def __create_buckets(self):
        if self.num_of_buckets > 0:
            self.__bucket_list = []
            for index in range(self.num_of_buckets):
                bucket_path = os.path.join(self.destination_path, 'bucket_{:03}'.format(index + 1))
                if CsvGenerator._create_dirs(bucket_path):
                    self.__bucket_list.append(bucket_path)

        return len(self.__bucket_list) == self.num_of_buckets


    def __create_csv_file(self, file_path):
        result = False
        if file_path:
            file_dir = os.path.dirname(file_path)
            CsvGenerator.__create_dirs(file_dir)
            with open(file_path, "w", newline='') as csv_file:
                writer = DictWriter(csv_file, delimiter=self.delimiter, fieldnames=["name", "phone", "address", "city", "state", "zip", "notes"])
                writer.writeheader()
                for _ in CsvGenerator.__random_enumerator():
                    writer.writerow({
                        'name': self.fake.name(),
                        'phone': self.fake.phone_number(),
                        'address': self.fake.street_address(),
                        'city': self.fake.city(),
                        'state': self.fake.state_abbr(),
                        'zip': self._fake.zipcode(),
                        'notes': self.fake.text(),
                    })

            result = os.path.isfile(file_path)

            if result:
                self.__file_list.append(file_path)

        return result

    def generate(self):
        pprint(self)

    # def generate(self, dynamic_num_of_files, path):
    #     # Using buckets
    #     # or
    #     # Using the current dir


    #     if self.num_of_buckets > 0:
    #         if self.__create_buckets():
    #             for bucket in self.__bucket_list:



    #     for index in range(self.num_of_files):
    #         file_name = self.path + "{:03}.csv".format(index + 1)

    #         if self.compress:
    #             with open(file_name, 'rb') as csv_file:
    #                 with gzip.open("{}.gz".format(file_name), 'wb') as gz_file:
    #                     copyfileobj(csv_file, gz_file)
    #             os.remove(file_name)



from argparse import ArgumentParser

if __name__ == '__main__':
    parser = ArgumentParser(description='Generate random files with some random content')
    parser.add_argument('-nf', '--num_of_files', metavar='N', type=int, default=1, help='Number of files to be generated')
    parser.add_argument('-nb', '--num_of_buckets', metavar='N', type=int, default=0, help='Number of buckets (extra dir) that are going to be created. If specified, each bucket will have a random number of files from 1 to the value specified on --files.')
    parser.add_argument('-dp', '--destination_path', default='.', help='Destination directory')
    parser.add_argument('-d', '--delimiter', type=str, metavar='D', default=',', help='Delimiter used to separate the records on files')
    parser.add_argument('-c', '--compress', type=bool, default=False, choices=[True, False], help='If true, the generated files will be compressed as .zip file. If the --buckets value is greater than zero will be created a zip file per bucket.')
    args = parser.parse_args()

    generator = CsvGenerator(
        num_of_files=args.num_of_files,
        num_of_buckets=args.num_of_buckets,
        destination_path=args.destination_path,
        delimiter=args.delimiter,
        compress=args.compress
    )

    print(generator)
