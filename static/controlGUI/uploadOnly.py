# -*- coding: utf-8 -*-
"""
Created on Fri May 19 07:59:22 2017

@author: Beau.Uriona
"""

from os.path import realpath
import subprocess as sub

basePath = realpath('./../../')
uploadScriptFileName = r'winSCPsync'
uploadScriptFile = basePath + r'\static\winSCPsync.txt'
ftpProgPath = r'C:\Program Files (x86)\WinSCP\WinSCP.com'
uploadScriptArg = r'/script=' + uploadScriptFile

print("Uploading Files...")
uploadRun = sub.Popen([ftpProgPath, uploadScriptArg])  
uploadExitCode = uploadRun.wait()

if uploadExitCode == 0:
    print("Done with NO errors")
else:
    print("Did not complete, error during upload!")
