#!/usr/bin/env python3
#-*- coding: utf-8 -*-
# Python Version 3.4 or above
# A tool for SM.MS Image Hosting API
# Example usage:
#   smms upload a.jpg b.png
#   smms find a.jpg
#   smms list
#   smms delete [id]
#   smms help
#   smms history [clean]
#
# API reference: https://sm.ms/doc/

import sqlite3
import os.path as opath
from pathlib import Path
import sys
import requests as rq
import json
import ntpath


def init():
    """
    Initialize a database and create a DB connection
    Returns a cursor
    """
    home = str(Path.home())
    db_file = home + "/.smms.sqlite3"

    existance = opath.exists(db_file)

    con = sqlite3.connect(db_file)
    cur = con.cursor()

    if existance is False:
        cur.execute("""CREATE TABLE smms (
                file_name varchar(256),
                url varchar(256),
                delete_url varchar(256)
                );""")

    return cur, con


def upload(cur, files):
    """
    The upload function.
    Args: files, list of files ['a.jpg', 'b.jpg']
    """
    if files is None:
        print("No file specified", file=sys.stderr)
        return

    api_url = "https://sm.ms/api/upload"

    for fil in files:
        files = {'smfile': open(fil, 'rb')}
        r = rq.post(api_url, files=files)
        jf = json.loads(r.text)
        if jf['code'] == 'success':
            # 1. Write to database
            url = jf['data']['url']
            delete = jf['data']['delete']
            file_name = ntpath.basename(fil)
            cur.execute("INSERT INTO smms (file_name, url, delete_url) VALUES\
                    ('%s', '%s', '%s')" % (file_name, url, delete))

            # 2. Output url
            print("Success!")
            print("Image URL: " + url)
            print("Image Delete URL: " + delete)
        else:
            print("File not found locally", file=sys.stderr)

def find(cur, patterns):
    """
    Find a pattern in the database from file_name
    """
    if patterns is None:
        print("No file specified", file=sys.stderr)
        return

    for pattern in patterns:
        cur.execute("SELECT rowid, file_name, url, delete_url FROM smms WHERE file_name\
                LIKE '%%%s%%'" % (pattern))
        items = cur.fetchall()

        for item in items:
            print(str(item[0]) + " " + item[1] + " " + item[2] + " " + item[3])


def delete(cur, image_ids):
    """
    Delete an image from SM.MS and also DB.
    image_ids is a list of image ids
    """
    if image_ids is None:
        print("No file specified", file=sys.stderr)
        return

    for i in image_ids:
        cur.execute("SELECT file_name, url, delete_url FROM smms WHERE rowid =\
                %s" % (i))
        item = cur.fetchone()

        if item is None:
            print("ID not found in the database.")
            return

        delete_url = item[2]
        r = rq.get(delete_url)

        print("Image deleted successfully")
        cur.execute("DELETE FROM smms WHERE rowid = %s" % (i))


def list_all(cur):
    """
    List all of the image in the database
    """
    cur.execute("SELECT rowid, file_name, url, delete_url FROM smms;")
    items = cur.fetchall()

    for item in items:
        print(str(item[0]) + " " + item[1] + " " + item[2] + " " + item[3])


def print_help():
    helptext="""This is an SM.MS Image Hosting API Commandline Interface tool
    To upload an image:
        smms upload a.jpg

    To upload a bunch of images:
        smms upload b.jpg c.jpg

    To list the files you uploaded
        smms list

    To delete a file you've uploaded, use image id
        smms delete 1

    To find a file original file name is a.jpg
        smms find a.jpg

    To print a list of uploaded files in the past hour, or to clean it
        smms history [clean]
    """
    print(helptext)


def history(action=None):
    list_url = "https://sm.ms/api/list"
    clear_url = "https://sm.ms/api/clear"
    if action is not None and action[0] == 'clear':
        rq.get(clear_url)
        print("History all cleared")
        return

    r = rq.get(list_url)
    rj = json.loads(r.text)
    if rj['code'] == 'success':
        for img in rj['data']:
            print(img['filename'] + " " + img['url'] + " " + img['delete'])
    else:
        print("API is unavailable", file=sys.stderr)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print_help()
        sys.exit(1)

    command = sys.argv[1]
    if command == 'help':
        print_help()
        sys.exit(0)

    if command not in ['delete', 'upload', 'find', 'list', 'history']:
        print("Command not supported.", file=sys.stderr)
        sys.exit(2)

    cur, con = init()
    arguments = sys.argv[2:] or None

    if command == 'delete':
        delete(cur, arguments)
    elif command == 'list':
        list_all(cur)
    elif command == 'upload':
        upload(cur, arguments)
    elif command == 'find':
        find(cur, arguments)
    elif command == 'history':
        history(arguments)
    else:
        pass

    cur.close()
    con.commit()
    con.close()
