#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 24 11:59:00 2020

@author: tonysafarik
"""
import md5compare

subset1_csv = '/Users/Shared/temp/dupeguru_home_edition/MiwaBookSubset1.csv'
subset1 = md5compare.csv_to_field_dict(subset1_csv,"md5","file path")

subset2_csv = '/Users/Shared/temp/dupeguru_home_edition/MiwaBookSubset2.csv'
subset2 = md5compare.csv_to_field_dict(subset2_csv,"md5","file path")

for i in subset1.keys():
    if len(subset1[i]) > 1:
        print (i)
        for j in subset1[i]: print (j)

# md5compare.combine_dict_list([subset1,subset2])

s1 = subset1.keys()
s2 = subset2.keys()

for md5 in s2:
    if md5 in s1:
        for i in subset2[md5]:
            print ('dupe')
            print(i)
            fpath = i
            src_folder = subset2_csv.replace('.csv','')
            dst_folder = subset2_csv.replace('.csv','_MOVED')
            new_fpath = fpath.replace(src_folder,dst_folder)
            print(fpath, new_fpath)
    else:
        print('NOT DUPE')
    # print ('______________')
