#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jul  5 16:07:47 2020

@author: anthonysafarik
"""

import os
import subprocess
import json
import csv
import time

now = time.strftime("%Y-%m-%d_%H%M%S")

class Library(object):
    """a place to hold media objects"""

    def __init__(self):
        """
        Initiates Library object
        media = dictionary of dictionaries. File paths are keys
        """
        self.media = {}

    def get_media(self):
        return self.media

    def get_media_list(self):
        """
        gets a list of paths from media keys and formats into a string

        Can be used as an argument for extracting ExifTool metadata
        """
        media_list = ''
        for i in self.media.keys():
            if media_list == '':
                media_list = i
            else:
                media_list = media_list+'\n'+i
            # media_list.append(i)
        return media_list

    def crawl_tree(self, directory, hiddenfiles = False):
        files_in_tree = {}
        for (path,dirs,files) in os.walk(directory):
            for item in files:
                this_dict = {}
                fp = os.path.join(path,item)
                if hiddenfiles == True or not item.startswith('.'):
                    file_name, file_extension = os.path.splitext(item)
                    this_dict['file path'] = fp
                    this_dict['file base name'] = file_name
                    this_dict['file name'] = item
                    this_dict['file extension'] = file_extension
                    this_dict['directory'] = path
                    this_dict['file size'] = os.path.getsize(fp)
                    this_dict['file modified time'] = os.path.getmtime(fp)
                    files_in_tree[fp] = this_dict
        return files_in_tree

    def print_media(self):
        for key in self.media.keys():
            print(self.media[key])

    def iter_media_keys(self):
        for entry in self.media.keys():
            yield self.media[entry].keys()

    def get_all_tags(self):
        all_tags = []
        for i in self.iter_media_keys():
            for j in i:
                if j not in all_tags:
                    all_tags.append(j)
        return all_tags

    def add_directory_to_media(self,inpath):
        dict = self.crawl_tree(inpath)
        self.media.update(dict)

    def add_exif_to_media(self,exif_metadata):
        """
        exif_metadata is a list of dicts as produced by ExifTool
        """
        print ('adding exif')
        for exif_dict in exif_metadata:

            try:
                file_path = exif_dict['SourceFile']
                print(file_path)
                if file_path in self.media.keys():
                    print('.....its a match to the key')
                    self.media[file_path].update(exif_dict)
                else:
                    print (self.media.keys())
            except KeyError:
                print('metadata is missing SourceFile information')

            if file_path in self.media.keys():
                self.media[file_path].update(exif_dict)

    def add_md5_to_media(self):
        """adds md5 for each file in media"""
        for fp in self.media.keys():
            if 'md5' not in self.media[fp].keys():
                output = subprocess.check_output(['MD5',self.media[fp]['file path']])
                output = output.decode('utf-8')
                md5 = output.split()[-1] #strip out the md5 part of the output string
                self.media[fp]['md5'] = md5
                print (self.media[fp]['file path'])
                print (self.media[fp]['md5'])
            else:
                print ('skipping md5',self.media[fp]['file path'])

    def dump_csv(self, csv_file):
        """
        csv_file: string representing the path to the csv file to write
        fieldnames: the list of headers to write to the csv_file
        list_of_dicts: each dictionary will looked up for each header and supply the values for one row of the csv_file.
        """

        list_of_dicts = self.media.values()
        fieldnames = self.get_all_tags()

        with open(csv_file, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for dict in list_of_dicts:
                writer.writerow(dict)

class ExifTool(object):
    """
    keeps exiftool open for speedy mass extraction of get_metadata

    from implementation on stackoverflow
    https://stackoverflow.com/questions/10075115/call-exiftool-from-a-python-script

    """
    sentinel = "{ready}\n"

    def __init__(self, executable="/usr/local/bin/exiftool"):
        self.executable = executable

    def __enter__(self):
        self.process = subprocess.Popen(
            [self.executable, "-stay_open", "True",  "-@", "-"],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        return self

    def  __exit__(self, exc_type, exc_value, traceback):
        self.process.stdin.write("-stay_open\nFalse\n".encode('utf-8'))
        self.process.stdin.flush()

    def execute(self, *args):
        args = args + ("-execute\n",)
        self.process.stdin.write(str.join("\n", args).encode('utf-8'))
        self.process.stdin.flush()
        output = ""
        fd = self.process.stdout.fileno()
        while not output.endswith(self.sentinel):
            output += os.read(fd, 4096).decode('utf-8')
        return output[:-len(self.sentinel)]

    def get_metadata(self, *filenames):
        return json.loads(self.execute("-G", "-j", "-n", *filenames))
###################TESTING####################

l = Library()
l.add_directory_to_media('/Users/anthonysafarik/Pictures/MediaFormats')
l.add_md5_to_media()

with ExifTool() as e:
    metadata = e.get_metadata(
    #'/Users/anthonysafarik/Pictures/MediaFormats/a7s.ARW\n/Users/anthonysafarik/Pictures/MediaFormats/a7s.JPG'
    l.get_media_list()
    )

l.add_exif_to_media(metadata)
for i in l.get_all_tags():
    print (i)

l.dump_csv('/Users/Shared/temp/'+now+'.csv')
########################################
#QuickTime:MajorBrand = mp42 = SM-J700T
#xxxRIFF:Software = CanonMVI03 = Canon PowerShot S3 IS
#xxxRIFF:VideoCodec = dvsd = digital8
#RIFF:DateTimeOriginal
#RIFF:DateCreated
#XMP:MetadataDate
#XMP:CreateDate
#XMP:ShotDate
#EXIF:DateTimeOriginal
#MakerNotes:SonyDateTime
#QuickTime:CreateDate
#QuickTime:TrackCreateDate
#QuickTime:MediaCreateDate
#XMP:DateCreated
#IPTC:DateCreated
#IPTC:TimeCreated
#Composite:DateTimeCreated
#XML:CreationDateValue
#EXIF:GPSDateStamp
#ICC_Profile:ProfileDateTime
#Composite:SubSecDateTimeOriginal
#QuickTime:CreationDate
#File:FileModifyDate
