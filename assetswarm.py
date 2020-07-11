#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jul  5 16:07:47 2020

a common interface for tracking files and metadata

image metadata extracting with exiftool
export/import to csv
dupe checking
rename files and folders

@author: anthonysafarik
"""

import os
import subprocess
import json
import csv
import time

now = time.strftime("%Y-%m-%d_%H%M%S")

class Library(object):
    """Library is a collection of files"""

    def __init__(self):
        """
        Initiates a Library object
        media = dictionary of dictionaries
                individual files are keys
                nested dictionaries contain named attributes
        groups = dictionary of lists
                keys representing attribute(s) to group by
        """
        self.media = {}
        self.groups = {}

    def get_media(self):
        return self.media

    def get_media_values(self):
        return self.media.values()

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
        return media_list

    def crawl_tree(self, directory, filterfiles = [] ,hiddenfiles = False):
        files_in_tree = {}
        for (path,dirs,files) in os.walk(directory):
            for item in files:
                this_dict = {}
                fp = os.path.join(path,item)
                if hiddenfiles == True or not item.startswith('.'):
                    file_name, file_extension = os.path.splitext(item)
                    this_dict['AssetSwarm:FilePath'] = fp
                    this_dict['AssetSwarm:FileBaseName'] = file_name
                    this_dict['AssetSwarm:FileName'] = item
                    this_dict['AssetSwarm:FileExtension'] = file_extension
                    this_dict['AssetSwarm:Directory'] = path
                    this_dict['AssetSwarm:FileSize'] = os.path.getsize(fp)
                    this_dict['AssetSwarm:FileModifyTime'] = os.path.getmtime(fp)
                    #check if we are supposed to be limiting the search to a certain file extension
                    if not filterfiles or file_extension.upper() in filterfiles:
                        files_in_tree[fp] = this_dict
        return files_in_tree

    def iter_media_keys(self): #do we need this?
        for entry in self.media.keys():
            yield self.media[entry].keys()

    def get_all_tags(self):
        all_tags = []
        for i in self.iter_media_keys(): #can this be simplified?
            for j in i:
                if j not in all_tags:
                    all_tags.append(j)
        return all_tags

    def add_directory_to_media(self, inpath, extenstions_to_filter=[]):
        """
        scours a folder on the file system and adds file paths as dictionary keys to media
        extenstions_to_filter is a list of the extentions to consider
        """
        dict = self.crawl_tree(inpath, extenstions_to_filter)
        self.media.update(dict)

    def add_exif_to_media(self,exif_metadata):
        """
        exif_metadata is a list of dicts as produced by ExifTool
        """
        print ('adding exif')
        for exif_dict in exif_metadata:

            try:
                file_path = exif_dict['SourceFile']
                if file_path in self.media.keys():
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
            if 'AssetSwarm:MD5' not in self.media[fp].keys() and 'AssetSwarm:FilePath' in self.media[fp].keys():
                output = subprocess.check_output(['MD5',self.media[fp]['AssetSwarm:FilePath']])
                output = output.decode('utf-8')
                md5 = output.split()[-1] #strip out the md5 part of the output string
                self.media[fp]['AssetSwarm:MD5'] = md5
            else:
                print ('skipping md5, value exists or missing file')

    def write_csv(self, csv_file, fieldnames, list_of_dicts):
        with open(csv_file, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for dict in list_of_dicts:
                writer.writerow(dict)

    def dump_csv(self, csv_file):
        """
        csv_file: string representing the path to the csv file to write
        fieldnames: the list of headers to write to the csv_file
        list_of_dicts: each dictionary will looked up for each header and supply the values for one row of the csv_file.
        """

        list_of_dicts = self.media.values()
        fieldnames = self.get_all_tags()
        self.write_csv(csv_file, fieldnames, list_of_dicts)

    def import_csv(self,csv_file,id_field='AssetSwarm:FilePath'):
        """
        imports csv and adds to media
        id_field is a field in the csv that is exepected to have a unique value for each row
        """
        dictreader = csv.DictReader(open(csv_file))
        print ('importing from',csv_file)
        for row in dictreader:
            fp = row[id_field]
            self.media[fp]=row

    def audition_asset_swarm_date(self):
        #TODO sometimes produces weird results, replace this method with something more controlled
        for fpath in self.media.keys():
            tags = self.media[fpath].keys()
            earliest_candidate = "30000000000000"
            this_tag = ''
            for tag in tags:
                if 'date' in tag.lower() and tag != "ASF:CreationDate":
                    print(fpath,self.media[fpath][tag],tag)
                    date_string = str(self.media[fpath][tag])

                    digits = ''
                    for char in date_string:
                        if char.isdigit():
                            digits = digits+char

                    if len(digits) >= 14:
                        this_tag = tag
                        date_slice = digits[0:13]
                        if int(date_slice) < int(earliest_candidate):
                            earliest_candidate = date_slice

            print (earliest_candidate,this_tag)
            self.media[fpath]['AssetSwarm:EarlyDate'] = earliest_candidate


class ExifTool(object):
    """
    keeps exiftool open for speedy mass extraction of get_metadata

    from implementation on stackoverflow
    https://stackoverflow.com/questions/10075115/call-exiftool-from-a-python-script

    make sure that you only feed media files into this

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
            try:
                output += os.read(fd, 4096).decode('utf-8')
            except UnicodeDecodeError:
                print ('skipping something')
        return output[:-len(self.sentinel)]

    def get_metadata(self, *filenames):
        return json.loads(self.execute("-G", "-j", "-n", *filenames))

###################TESTING####################

# l = Library()
# l.add_directory_to_media('/Volumes/Seagate8TB/DATA/Photos/2004',['.ARW','.JPG','.MP4','.MOV','.ASF'])
# l.add_md5_to_media()
#
# with ExifTool() as e:
#     metadata = e.get_metadata(
#     l.get_media_list()
#     )
#
# l.add_exif_to_media(metadata)
# l.audition_asset_swarm_date()
# l.dump_csv('/Users/Shared/temp/'+now+'.csv')

##############################################

# l.import_csv('/Users/Shared/temp/'+now+'.csv')
# media = l.get_media()
# for i in media:
#     ed = media[i]['AssetSwarm:EarlyDate']
#     # print (ed)
#     easy = ed[0:4]+'-'+ed[4:6]+'-'+ed[6:8]
#     # print (easy)
#     folder = os.path.split(media[i]['AssetSwarm:Directory'])[-1]
#     if folder != easy:
#         print ('no match',folder,easy)

##############################################

#down and dirty way to compare two lists

# l = Library()
# l.import_csv('/Users/anthonysafarik/Downloads/Version.csv','Version Name')
# media = l.get_media()
# sg_versions = []
# for key in media.keys():
#     sg_versions.append(key.upper())
#
# edl = Library()
# edl.import_csv('/Users/anthonysafarik/Git/tom-edl/101_top_versions_lineup.csv','Version Name')
#
# edl_media = edl.get_media()
# edl_versions = []
# for key in edl_media.keys():
#     edl_versions.append(key.replace('.MOV',''))
#
# for i in sg_versions:
#     if i not in edl_versions:
#         print (i)



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
