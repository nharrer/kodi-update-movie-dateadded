# kodi-update-movie-dateadded

A Python script which fixes messed up "Date Added" fields of any video files in Kodi.

Notes
-----

 - This is not a Kodi AddOn. It’s just a simple python script that manipulates the sqlite video database directly. So handle with care, and back up your video database.
 - Also exit Kodi before you run this script.
 - This script was tested with Kodi 20.1
 - Change the location of your video database in the script accordingly. If you don’t know where it is, check this Kodi Wiki Entry about Userdata location.
 - If the script does not find file names with special characters, you might change the encoding from 'cp1252' to whatever you have. cp1252 is the standard encoding in windows for Western Europe.

SQLite3
-----

You need py-sqlite3 library installed on your system for the script to open the database.

MySQL
-----

Users who use a Kodi/MySQL setup need to change the setting to MYSQL = True and set the other MYSQL-settings accordingly.
Also make sure to download and install the Python MySQL package: https://pypi.python.org/pypi/MySQL-python/1.2.5

