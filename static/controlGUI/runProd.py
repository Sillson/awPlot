#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 20 09:12:57 2017

@author: Beau.Uriona
"""

from os import listdir
from os.path import isfile, join, dirname, abspath
import subprocess as sub
from multiprocessing.dummy import Pool
from datetime import datetime
from string import Template

dt = datetime
date = dt.date
today = dt.now()
this_dir = dirname(abspath(__file__))
master_dir = dirname(dirname(this_dir))
logFile = join(master_dir,'static','runLog.txt')
statusFile = join(master_dir,'static','prodStatus.html')
scriptPath = join(master_dir,'prodScripts')

class DeltaTemplate(Template):
    delimiter = "%"    
def run(runfile):
    with open(runfile, "r") as rnf:
        exec(rnf.read())
def writeToLog(strLog):
    with open(logFile, 'r+') as loggerFile:
        content = loggerFile.read()
        loggerFile.seek(0, 0)
        loggerFile.write(strLog + '\n\n' + content)
def writeToProdStatus(strLog):
    with open(statusFile, 'w') as loggerFile:
        loggerFile.write(strLog)
def strfdelta(tdelta, fmt):
    d = {"D": tdelta.days}
    hours, rem = divmod(tdelta.seconds, 3600)
    minutes, seconds = divmod(rem, 60)
    d["H"] = '{:02d}'.format(hours)
    d["M"] = '{:02d}'.format(minutes)
    d["S"] = '{:02d}'.format(seconds)
    t = DeltaTemplate(fmt)
    return t.substitute(**d)

def stopProduction():
    global keepRunning
    keepRunning = False
    
def runProduction():
    global keepRunning
    keepRunning = True
    cycles = 0
    
    while keepRunning:
        
        beginScript = datetime.now()
        scriptNames = [f.replace(r'.py',r'') for f in listdir(scriptPath) if 
                      isfile(join(scriptPath, f)) and f[-3: ] == r'.py']
        
        runScripts = [[r'python', join(scriptPath, f)] for 
                       f in listdir(scriptPath) if 
                      isfile(join(scriptPath, f)) and f[-3: ] == r'.py']
    
        print('Begin Scripts @ - ' + datetime.now().strftime('%H:%M:%S'))
        print(r'Running scripts located in - ' + scriptPath)
        
        exitCodes = []
        pool = Pool(4) # four concurrent commands at a time
        for i, exitCode in enumerate(pool.imap(sub.call, runScripts)):
            exitCodes.extend([exitCode])
            if exitCode == 0:
                print("%s  - SUCCESS!" % 
                      (runScripts[i][1].replace(scriptPath,r'').replace('\\',r'')))
            if exitCode != 0:
                print("%s  - FAILED: %d" % 
                      (runScripts[i][1].replace(scriptPath,r'').replace('\\',r''),
                       exitCode))
        
        if cycles == 0: errCodeSum = [0]*(len(exitCodes)+1)
        endScript = datetime.now()
          
        scriptRunTime = strfdelta(endScript - beginScript, '%H:%M:%S')
        
        joinStr = '\n\t'
        iterLog = joinStr.join(["%s - %s" % f for f in zip(scriptNames,exitCodes)])
        logStr = (r'Script Start - ' + beginScript.strftime('%H:%M:%S') +
                  joinStr + iterLog + '\n' + '\nScript Time - ' + scriptRunTime) 
        
        writeToLog(logStr)
        htmlStr = r'''<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN"
        "http://www.w3.org/TR/html4/loose.dtd"> <html lang="en"> <head>
        <meta http-equiv="content-type" content="text/html; charset=utf-8">
        <title>iChart Production Status</title> </head> <body> <p>REPLACE</p>
        </body> </html>'''

        # Perhaps change to a yield block above? 
        
        htmlStr = htmlStr.replace(r'REPLACE', logStr)
        htmlStr = htmlStr.replace('\n', r'<br>')
        htmlStr = htmlStr.replace('\t', r'<LI>')
        writeToProdStatus(htmlStr)

        # HTML scrub or encode methods? perhaps there is a library for this
        
        currErrCodes = list(exitCodes)
        for index, err in enumerate(currErrCodes):
            if err != 0:
                errCodeSum[index] = errCodeSum[index] + 1
            else:
                errCodeSum[index] = 0
        
        if max(errCodeSum) > 0:
            print('Completed with errors @ - ' +
                  datetime.now().strftime('%H:%M:%S'))
        else:
            print('Completed with NO errors @ - ' +
                  datetime.now().strftime('%H:%M:%S'))
        
        print(r'!@#$' + logStr + r'!@#$')
            
        if sum(errCodeSum) != 0 and cycles < 10:
            keepRunning = True
        else:
            keepRunning = False
            if cycles == 10:
                writeToLog('****After 10 attempts the process was aborted****')
                
        cycles += 1
if __name__ == "__main__":
    runProduction()