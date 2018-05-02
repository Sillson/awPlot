# -*- coding: utf-8 -*-
"""
Created on Tue May  9 08:42:44 2017

@author: Beau.Uriona
"""
import os
import ctypes  # An included library with Python install.
def Mbox(title, text, style):
    result = ctypes.windll.user32.MessageBoxW(0, text, title, style)
    return result
rootDir = '..'
cnt = 0
msg = ('Are you sure you want to delete all html pages in:\n\n ' + 
       os.path.abspath(rootDir) + "\n\n ...and all it's sub-directories")
response = Mbox('Caution!', msg, 4)

if response == 6:
    for dirName, subdirList, fileList in os.walk(rootDir):
        if len(list([f for f in fileList if f.endswith(r'.html')])) > 0:
                for fname in fileList:
                    if fname.endswith('.html'):
                        cnt += 1
                        os.remove(os.path.join(dirName,fname))