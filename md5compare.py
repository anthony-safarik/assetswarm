#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 24 11:59:00 2020

@author: tonysafarik
"""
import csv
import os

def combine_dict_list(dict_list):
    """dict_list is a list of dictionaries with values that are lists. this will combine several lists into one dict"""
    new_dict = {}
    for dict in dict_list:
        print ('next')
        for key in dict.keys():
            print(key)
            if not key in new_dict.keys():
                new_dict[key] = dict[key]
                #NOT FINISHED OR USED

def csv_to_field_dict(csv_file,key_field,list_field,):
    """
    finds duplicate entries for an ID field in a csv file and makes a list of values from some secondary field
    opens csv_file and returns field_dict
    field_dict is a dictionary keyed to the values for key_field and listing the values in list_field
    """
    field_dict = {}
    csv_dictreader = csv.DictReader(open(csv_file))
    for row in csv_dictreader:
        new_value = row[list_field]
        new_key = row[key_field]
        # print(new_key)
        try:
            if field_dict[new_key]:
                # print('yes dupe!')
                field_dict[new_key].append(new_value)
        except KeyError:
            field_dict[new_key] = [new_value]
    return field_dict

def main(src_dir,dst_dir):
    """
    made to validate copies, this compares two csv files src_dir and dst_dir
    reports whether all the files in dst_dir are also in src_dir
    """
    src_md5_list = []
    dst_md5_list = []
    src_dictreader = csv.DictReader(open(src_dir))
    dst_dictreader = csv.DictReader(open(dst_dir))

    for row in dst_dictreader:
        dst_md5_list.append(row['md5'])

    clear = True

    for row in src_dictreader:
        src_md5_list.append(row['md5'])
        if row['md5'] not in dst_md5_list:
            print(row['file path'],'not in dst')
            clear = False

    if clear: print ('all files in',src_dir, "are in", dst_dir)

#####TESTING######
src_dir = input('enter source folder csv').strip()
dst_dir = input('enter copied folder csv').strip()
if os.path.exists(src_dir) and os.path.exists(dst_dir):
    main(src_dir,dst_dir)
