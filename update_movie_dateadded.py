import sys
import os
import re
import time
import datetime
from contextlib import closing

# ---------------------------------------------------
# Settings
# ---------------------------------------------------

# IMPORTANT: In the standard case (sqlite3) just point this to your own MyVideos database.
DATABASE_PATH = os.path.join(r"C:\Users\<Your User>\AppData\Roaming\Kodi\userdata\Database", 'MyVideos90.db')

# Or if you're using MySQL as a database, change MYSQL to True and change the other MySQL settings accordingly.
# Also make sure to install the MySQL python package: https://pypi.python.org/pypi/MySQL-python/1.2.5
MYSQL = False
MYSQL_USER = "kodi"
MYSQL_PASS = "kodi"
MYSQL_SERVER = "localhost"
MYSQL_DATABASE  = "MyVideos90"

# Set this to True to get more verbose messages
VERBOSE = False

# ---------------------------------------------------
# Constants
# ---------------------------------------------------

stack_regex = re.compile("stack://(.*?)\s*[,$]")
date_format = '%Y-%m-%d %H:%M:%S'

col_id = 'idFile'
col_filename = 'strFileName'
col_path = 'strPath'
col_dateadded = 'dateAdded'

# ---------------------------------------------------
# Functions
# ---------------------------------------------------

def die(message):
    sys.stderr.write(message)
    sys.exit(-1)

def open_database():
    if MYSQL:
        import MySQLdb.cursors
        connection = MySQLdb.connect(
            host=MYSQL_SERVER,   # name or ip of mysql server
            user=MYSQL_USER,     # your username
            passwd=MYSQL_PASS,   # your password
            db=MYSQL_DATABASE,   # name of the database
            cursorclass=MySQLdb.cursors.DictCursor)
        print "DB connection opened to {0}@{1}.".format(MYSQL_DATABASE, MYSQL_SERVER)
    else:
        try:
            from sqlite3 import dbapi2 as sqlite
            print "Loading sqlite3 as DB engine"
        except:
            from pysqlite2 import dbapi2 as sqlite
            print "Loading pysqlite2 as DB engine"

        connection = sqlite.connect(DATABASE_PATH)
        #connection.text_factory = str
        connection.text_factory = lambda x: unicode(x, 'utf-8', 'ignore')
        connection.row_factory = sqlite.Row
        print "DB connection opened to {0}.".format(DATABASE_PATH)
    return connection

def check_column(columns, columnname):
    if not columnname in columns:
        die('Table does not contain column {0}!!'.format(columnname))
    
def process_row(conn, row):
    keys = row.keys()

    filename = row[col_filename]
    path = row[col_path]
    id = row[col_id]

    filename = filename.encode('cp1252')
    path = path.encode('cp1252')
    
    stack = stack_regex.findall(filename)
    if (len(stack) > 0):
        fullpath = stack[0]
    else:
        fullpath = os.path.join(path, filename)

    if not os.path.isfile(fullpath):
        print('File {0} does not exist!'.format(fullpath))
        return

    lastmod = os.path.getmtime(fullpath)
    #if lastmod < 0 or lastmod > 4102444800L:
    #    lastmod = os.path.getctime(fullpath)                            

    if lastmod < 0 or lastmod > 4102444800L:
        print("Ignoring File {0}. Date is out of range (lastmod={1})".format(fullpath, lastmod))
        return

    lt = time.localtime(lastmod)
    dateadded_new = time.strftime(date_format, lt)

    dateadded = str(row[col_dateadded])

    if dateadded != dateadded_new:
        print('idFile {0}: {1} -> {2} ({3})'.format(id, dateadded, dateadded_new, fullpath))
        with closing(conn.cursor()) as cursor:
            cursor.execute("UPDATE files SET dateAdded = '{0}' WHERE idFile = {1}".format(dateadded_new, id))
            conn.commit()
    else:
        if VERBOSE:            
            print('idFile {0}: Date OK. DB date {1} matches file date {2} ({3})'.format(id, dateadded, dateadded_new, fullpath))
        
# ---------------------------------------------------
# Main
# ---------------------------------------------------

conn = open_database()
cursor = conn.cursor()

with closing(conn.cursor()) as cursor:
    cursor.execute('SELECT idMovie, idFile, strFileName, strPath, dateAdded FROM movieview ORDER BY idFile')
    columns = map(lambda x: x[0], cursor.description)
    rows = cursor.fetchall()

check_column(columns, col_id)
check_column(columns, col_filename)
check_column(columns, col_path)
check_column(columns, col_dateadded)
print "Columns checked. They are ok."

for row in rows:
    process_row(conn, row)

print "Processed {0} Rows.".format(len(rows))
