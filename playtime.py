# -*- coding: utf-8 -*-
import argparse
import os
import plistlib
import sys
import operator
from unidecode import unidecode

ALIAS_DICT = {
    'MF Doom': ['Doom','MF Doom','Danger Doom','King Geedorah','Madvillain','Viktor Vaughn'],
}

XML_PATH = 'path/to/MusicBee/iTunes Music Library.xml'

def time_to_human(seconds):
    """
    Convert time in seconds to human readable format.
    
    :returns: a string of the form "DD days, HH hours, MM minites and
    SS seconds".
    """
    assert seconds >= 0, "number of seconds should be nonnegative"
    dd = int(seconds) // 86400 # days
    hh = (int(seconds) // 3600) % 24 # hours
    mm = (int(seconds) // 60) % 60 # minutes
    ss = seconds - (int(seconds) // 60) * 60 # seconds
    
    text = ""
    if dd:
        text += "%d days, " % dd
    if hh:
        text += "%d hours, " % hh
    if mm:
        text += "%d min, " % mm
    if ss:
        text += "%d sec" % ss
    
    return text
    
def get_alias(name):
    """
    Return any known alias for a given name, otherwise return the given name.
    
    :param name: String of name to check for aliases.
    :returns: Alias string if found, else the name given.
    """
    for alias,aka_list in ALIAS_DICT.items():
        if name in aka_list:
            return alias
    return name

def itunes_total_time(library_plist=None, tag_key="Album Artist", optional_key=None):
    """
    Prints the time spent on each track grouped by tag_key.
    
    :param library_plist: path to the iTunes Music Library plist file
    """

    with open(library_plist, "rb") as fp:
        tree = plistlib.load(fp) # the XML tree

    if 'Tracks' not in tree:
        return 0

    time_dict = {}
    count_dict = {}
    for _, track in tree['Tracks'].items():
        try:
            if 'Album Artist' not in track:
                print("missing album artist",unidecode(track['Artist']),unidecode(track['Name']))
            if 'audio' in track['Kind'] and 'Total Time' in track and 'Play Count' in track:
                curr_key = track[tag_key]
                curr_key = get_alias(curr_key)
                
                if optional_key:
                    curr_key += " (" + get_alias(track[optional_key]) + ")"

                if curr_key not in time_dict:
                    time_dict[curr_key] = 0
                    count_dict[curr_key] = 0
                time_dict[curr_key] += track['Total Time'] * track['Play Count'] # milliseconds
                count_dict[curr_key] += track['Play Count']
            else:
                #print("skipping",unidecode(track['Artist']),unidecode(track['Name']))
                pass
        except KeyError:
            pass
    
    #Print each time
    sorted_times = sorted(time_dict.items(), key=operator.itemgetter(1))
    for curr_key,time in sorted_times:
        time = time / 1000
        time_human = time_to_human(time)
        print("%s: %.0f sec (%s) with %s plays (%s avg)" % (unidecode(curr_key), time, time_human, count_dict[curr_key], time_to_human(time/count_dict[curr_key])))
    
    #Print a total
    total_count = sum(count_dict.values())
    total_time = sum(time_dict.values()) / 1000
    total_time_human = time_to_human(total_time)
    print("Total: %.0f sec (%s) with %s plays (%s avg)" % (total_time, total_time_human, total_count, time_to_human(total_time/total_count)))

def main(file_path):
    """
    Prints the time listened by Album then by Album Artist.
    
    :param file_path: String of library xml.
    """
    try:
        print("------\nALBUM\n------")
        total_time = itunes_total_time(file_path, tag_key="Album", optional_key="Album Artist")
        print("------\nARTIST\n------")
        total_time = itunes_total_time(file_path)
    except FileNotFoundError as err:
        print(err, file=sys.stderr)
        exit(1)
    input("continue")
    

if __name__ == '__main__':
    main(XML_PATH)