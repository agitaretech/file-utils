#!/usr/bin/env python

"""
.. module:: file_utils.py
:platform: Unix, Windows
:synopsis: Set of scripts used to manipulate files on the local file system
.. moduleauthor:: Toddy Mladenov <toddysm@agitaretech.com>
"""

import logging
import os
import os.path
from shutil import copyfile

# use default logging configuration
logger = logging.getLogger('at.utils.file_utils')
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
logger.addHandler(handler)
    
class iStr(str):
    """Case insensitive strings class.
    Behaves like normal str except comparisons are case insensitive.
    
    .. note::
    This class is courtesy of [Activestate](http://code.activestate.com/recipes/194371-case-insensitive-strings/)"""

    def __init__(self, strMe):
        str.__init__(self, strMe)
        self.__lowerCaseMe = strMe.lower()

    def __repr__(self):
        return "iStr(%s)" % str.__repr__(self)

    def __eq__(self, other):
        return self.__lowerCaseMe == other.lower()

    def __lt__(self, other):
        return self.__lowerCaseMe < other.lower()

    def __le__(self, other):
        return self.__lowerCaseMe <= other.lower()

    def __gt__(self, other):
        return self.__lowerCaseMe > other.lower()

    def __ne__(self, other):
        return self.__lowerCaseMe != other.lower()

    def __ge__(self, other):
        return self.__lowerCaseMe >= other.lower()

    def __cmp__(self, other):
        return cmp(self.__lowerCaseMe, other.lower())

    def __hash__(self):
        return hash(self.__lowerCaseMe)

    def __contains__(self, other):
        return other.lower() in self.__lowerCaseMe

    def count(self, other, *args):
        return str.count(self.__lowerCaseMe, other.lower(), *args)

    def endswith(self, other, *args):
        return str.endswith(self.__lowerCaseMe, other.lower(), *args)

    def find(self, other, *args):
        return str.find(self.__lowerCaseMe, other.lower(), *args)
    
    def index(self, other, *args):
        return str.index(self.__lowerCaseMe, other.lower(), *args)

    def lower(self):    # Courtesy Duncan Booth
        return self.__lowerCaseMe

    def rfind(self, other, *args):
        return str.rfind(self.__lowerCaseMe, other.lower(), *args)

    def rindex(self, other, *args):
        return str.rindex(self.__lowerCaseMe, other.lower(), *args)

    def startswith(self, other, *args):
        return str.startswith(self.__lowerCaseMe, other.lower(), *args)

def copy_recursively(src, dest, ext=None):
    """Recursively copies the files with the specified extension from the source
    folder to the destination folder.
    The function recursively iterates the list of files in the source folder and
    its subfolders and if the extension matches copies the file to the destination
    location. The filename is modified by a sequence number if it already exists
    in the destination folder.
    By default the function copies all the files from the source tree.
    :param src: The source folder where the original files are located
    :type src: string
    :param dest: The destination folder where the files should be stored
    :type dest: string
    :param ext: The file extension for the files to copy. Default is `None`
    :type ext: string
    """
    file_counter = 0
    for root, subFolders, files in os.walk(src):
        for filename in files:
            # get the extension without the dot
            extension = iStr(os.path.splitext(filename)[1][1:])
            if ext is None or extension == ext:
                src_path = os.path.join(root, filename)
                dest_path = os.path.join(dest, filename)
                
                # modify the destination filename in order not ot overwrite
                seq = 0 # use as a sequence counter
                while os.path.isfile(dest_path):
                    dest_path = os.path.join(dest, os.path.splitext(filename)[0] + \
                                             str(seq) + os.path.splitext(filename)[1])
                    seq += 1
                    
                copyfile(src_path, dest_path)
                file_counter += 1
    
    logger.info("%d files copied", file_counter)

def rename_sequencial(src, stem, padding=5, start_num=0):
    """Renames the files in the source folder using unified names with the
    following scheme:
    `[stem]_[NNNNN].[EXT]`
    Where:
    * `stem` - text based file name stem
    * `NNNNN` - zero padded sequence number
    * `EXT` - the original file extension
    :param src: The source folder where the files are located
    :type src: string
    :param padding: The length of the zero padded number added to the file name.
    Default is 5
    :type padding: int
    :param start_num: The starting number for the sequence
    :type start_num: int
    """
    seq = start_num
    
    for item in os.listdir(src):
        if os.path.isfile(os.path.join(src, item)):
            new_name = os.path.join(src, stem + "_" + str(seq).zfill(padding) + \
                                    os.path.splitext(item)[1])
            os.rename(os.path.join(src, item), new_name)
            seq += 1
    
    logger.info("%d files renamed", seq)

def list_files(src, mode="simple", loc="files_list.csv", sep=","):
    """Creates a coma separated list of the files in the source folder.
    :param src: The source folder where the files are located
    :type src: string
    :param mode: The mode of data generation. Can be:
    * `simple` - only file names are listed
    * `full` - path, filename, filesize and modification time (in seconds) are listed
    :type mode: string
    :param loc: Path to save the resulting list
    :type loc: string
    :param sep: The separator to use. Can be `,` (default) or `\t`
    :type sep: string    
    """
    with open(loc, "w") as f:
        # write the header
        if mode == 'simple':
            line = "file_name"
        elif mode == 'full':
            line = "location" + sep + "filename" + sep + "size" + sep + \
                   "last_modified"
        line += "\n"
        f.write(line)

        for item in os.listdir(src):
            file_path = os.path.join(src, item)
            # list only files
            if os.path.isfile(file_path):
                if mode == 'simple':
                    line = item
                elif mode == 'full':
                    file_info = os.stat(file_path)
                    line = src + sep + item + sep + str(file_info.st_size) + sep + \
                           str(file_info.st_mtime)
                line += "\n"
                f.write(line)