SM.MS CLI
====

Required: Python Version 3.4 or above, tested under Linux, use requests module

Description
---

A tool for SM.MS Image Hosting API

Example usage:
---

    smms upload a.jpg b.png
    smms find a.jpg
    smms list
    smms delete [id]
    smms help
    smms history [clean]

API reference: https://sm.ms/doc/

Install
---
sudo cp main.py /usr/local/bin/smms


upload
---

Upload an image, will output a direct link and a delete link.

find
---
Find an image using a wilcard pattern. For example:

    smms find scr

This will search for all your historical upload for `*scr*` in the original file name.

list
---
List all your images you've uploaded which has not been deleted via this cli
tool.

delete
---
Delete the image ID you specified in the local database.

help
---
Show the help message

history
---
Show the history of your upload (via SM.MS API) in the past 1 hour.

Provide the `clear` argument to clear the history from SM.MS.
