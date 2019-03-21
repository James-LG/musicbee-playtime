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
    assert seconds >= 0 #number of seconds should be nonnegative
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
    
    :param library_plist: path to the iTunes Music Library plist file.
    :param tag_key: Metadata tag to group by.
    :param optional_key: Add a tag to the grouped tag for readability.
    :returns: List of tuples ordered by time where the tag_key is the first item and a dict with time, time_human, avg_time_human and count is stored.
    """

    with open(library_plist, "rb") as fp:
        tree = plistlib.load(fp) # the XML tree

    if 'Tracks' not in tree:
        return 0

    tag_dict = {}
    for track in tree['Tracks'].values():
        try:
            if tag_key not in track:
                print("missing " + tag_key + " tag",unidecode(track['Artist']),unidecode(track['Name']))
            if 'audio' in track['Kind'] and 'Total Time' in track and 'Play Count' in track:
                curr_key = track[tag_key]
                curr_key = get_alias(curr_key)
                
                if optional_key:
                    curr_key += " (" + get_alias(track[optional_key]) + ")"

                if curr_key not in tag_dict:
                    tag_dict[curr_key] = {'time':0, 'count':0}
                tag_dict[curr_key]['time'] += track['Total Time'] * track['Play Count'] / 1000
                tag_dict[curr_key]['count'] += track['Play Count']
            else:
                #print("skipping",unidecode(track['Artist']),unidecode(track['Name']))
                pass
        except KeyError:
            pass

    # Add a total
    total_count = sum(x['count'] for x in tag_dict.values())
    total_time = sum(x ['time'] for x in tag_dict.values())
    tag_dict['Total Time'] = {'time': total_time, 'count': total_count}
    
    #Print each time
    sorted_times = sorted(tag_dict.items(), key=lambda kv: kv[1]['time'])
    for curr_key, curr_dict in sorted_times:
        time_human = time_to_human(curr_dict['time'])
        curr_dict['time_human'] = time_human
        curr_dict['avg_time_human'] = time_to_human(curr_dict['time']/curr_dict['count'])
    
    return sorted_times

def print_sorted(sorted_times):
    for curr_key, curr_dict in sorted_times:
        print("%s: %.0f sec (%s) with %s plays (%s avg)" % (unidecode(curr_key), curr_dict['time'], curr_dict['time_human'], curr_dict['count'], curr_dict['avg_time_human']))

def main(file_path=XML_PATH):
    """
    Prints the time listened by Album then by Album Artist.
    
    :param file_path: String of library xml.
    """
    try:
        print("------\nALBUM\n------")
        print_sorted(itunes_total_time(file_path, tag_key="Album", optional_key="Album Artist"))
        print("------\nARTIST\n------")
        print_sorted(itunes_total_time(file_path))
    except FileNotFoundError as err:
        print(err, file=sys.stderr)
        exit(1)
    input("continue")
    

if __name__ == '__main__':
    main()