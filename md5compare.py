#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 24 11:59:00 2020

@author: tonysafarik
"""
import csv

def main(src_dir,dst_dir):
    src_md5_list = []
    dst_md5_list = []
    src_dictreader = csv.DictReader(open(src_dir))
    dst_dictreader = csv.DictReader(open(dst_dir))

    for row in dst_dictreader:
        dst_md5_list.append(row['md5'])

    for row in src_dictreader:
        src_md5_list.append(row['md5'])
        if row['md5'] not in dst_md5_list:
            print(row['file path'],'not in dst')

#####TESTING######
src_dir = input('enter source folder csv').strip()
dst_dir = input('enter copied folder csv').strip()
main(src_dir,dst_dir)
