import sys
import os
import re
import time
import datetime
from contextlib import closing

try:
    from sqlite3 import dbapi2 as sqlite
    print "Loading sqlite3 as DB engine"
except:
    from pysqlite2 import dbapi2 as sqlite
    print "Loading pysqlite2 as DB engine"

# ---------------------------------------------------
# Constants
# ---------------------------------------------------

# IMPORTANT: Change this to your own MyVideos DB
DB = os.path.join(r"D:\working", 'MyVideos90.db')

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

    # path fix for LakersFan
    if fullpath.startswith('smb:'):
        fullpath = fullpath[4:]
    fullpath = os.path.abspath(fullpath)

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

    dateadded = row[col_dateadded]

    if dateadded != dateadded_new:
        print('idFile {0}: {1} -> {2} ({3})'.format(id, dateadded, dateadded_new, fullpath))
        with closing(conn.cursor()) as cursor:
            cursor.execute("UPDATE files SET dateAdded = '{0}' WHERE idFile = {1}".format(dateadded_new, id))
            conn.commit()
    else:   
        print('idFile {0}: Date OK. DB date {1} matches file date {2} ({3})'.format(id, dateadded, dateadded_new, fullpath))

# ---------------------------------------------------
# Main
# ---------------------------------------------------

conn = sqlite.connect(DB)
#conn.text_factory = str
conn.text_factory = lambda x: unicode(x, 'utf-8', 'ignore')
conn.row_factory = sqlite.Row

cursor = conn.cursor()
print "DB connection to {0} opened.".format(DB)

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
