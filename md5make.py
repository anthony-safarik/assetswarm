import os
import hashlib
import csv

def get_md5(inpath):
    """
    assumes inpath is a valid path to a file
    returns the md5 value for the file
    NEEDS TO BE FIXED, THIS IS NOT PRODUCING PROPER MD5S
    """
    hash_md5 = hashlib.md5()
    with open(inpath, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def get_file_path_list(inpath):
    """
    walks directory "inpath" and returns a list of files
    """
    dir_list=[]
    for (path,dirs,files) in os.walk(inpath):
        for item in files:
            dir_list.append(os.path.join(path,item))
    return sorted(dir_list)

def build_md5_dicts(file_path_list):
    """
    accepts a list of file paths, and creates a dictionary for each file
    keys = 'file path', 'md5'
    returns a list of dictionaries
    """
    md5_dicts = []
    for file_path in file_path_list:
        md5_dict = {}
        md5_dict['file path'] = file_path
        md5_dict['md5'] = get_md5(file_path)
        md5_dicts.append(md5_dict)
    return md5_dicts

def write_csv(csv_file, fieldnames, list_of_dicts):
    """
    csv_file: string representing the path to the csv file to write
    fieldnames: the list of headers to write to the csv_file
    list_of_dicts: each dictionary will looked up for each header and supply the values for one row of the csv_file.
    """
    with open(csv_file, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for dict in list_of_dicts:
            writer.writerow(dict)

def main(inpath):
    """requires inpath as an argument and creates csv file of folder contents inpath.csv"""
    if os.path.isdir(inpath):
        fieldnames = ['file path', 'md5']
        inpath_file_path_list = get_file_path_list(inpath)
        md5_dicts = build_md5_dicts(inpath_file_path_list)
        csv_file = inpath+'.csv'
        write_csv(csv_file, fieldnames, md5_dicts)
        if os.path.exists(csv_file): print(csv_file)

#####TESTING######
# inpath = input('enter source folder')
# main(inpath)
