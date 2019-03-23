# musicbee-playtime
Simple Python script to calculate total album and track playtime for MusicBee

# Use
First you must enable MusicBee > Preferences > Library > [Check] export the library as an iTunes formatted XML file

The file will be created in C:\Users\USER\Music\MusicBee\iTunes Music Library.xml
Set this value as XML_PATH in the script and run.

The ALIAS_DICT is used for artists that go by multiple names.
The key is the name they should be grouped under, and the value is a list of aliases.
Make sure the key is itself in the list of aliases.

# Requirements
Python obviously
unidecode: Used to prevent strange characters from crashing during print.
