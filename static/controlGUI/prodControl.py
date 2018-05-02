#!/usr/bin/env python
#-*- coding:utf-8 -*-

import time
from PyQt5 import QtCore, QtWidgets, QtGui, uic
from os.path import realpath
from os import startfile
import sys
import runProd

basePath = realpath('./../../')
logFile = basePath + r'\static\runLog.txt'
prodFile = basePath + r'\runProdTest.py'
batFile = basePath + r'\runProd.bat'#.replace('\\','/')

class EmittingStream(QtCore.QObject):

    textWritten = QtCore.pyqtSignal(str)

    def write(self, text):
        self.textWritten.emit(str(text))
 
class timerThread(QtCore.QThread):
    timeElapsed = QtCore.pyqtSignal(int)

    def __init__(self, parent=None):
        super(timerThread, self).__init__(parent)
        self.timeStart = None

    def start(self, timeStart):
        self.timeStart = timeStart

        return super(timerThread, self).start()
    
    @QtCore.pyqtSlot()
    def run(self):
        while self.parent().isRunning():
            self.timeElapsed.emit(time.time() - self.timeStart)
            time.sleep(1)

class myThread(QtCore.QThread):
    timeElapsed = QtCore.pyqtSignal(int)
    terminalText = QtCore.pyqtSignal(str)
    def __init__(self, parent=None):
        super(myThread, self).__init__(parent)

        self.timerThread = timerThread(self)
        self.timerThread.timeElapsed.connect(self.timeElapsed.emit)
        
    def resetTime(self):
        self.timerThread.start(time.time())
        
    def run(self):
        self.timerThread.start(time.time())
        runProd.runProduction()
        
class prodStatus(QtWidgets.QDialog):    
    def __init__(self):
        super(prodStatus, self).__init__() 
        
        uic.loadUi(r'controlGUI.ui', self)
        self.show()
        
        self.cmdStartProd.setCheckable(True)
        self.cmdStartProd.setStyleSheet(
                "QPushButton:checked {background-color:" + 
                " Chartreuse; border: None}")
        self.cmdStartProd.clicked.connect(self.startProd)

        self.cmdOpenLog.clicked.connect(self.openLog)
        
        self.lcdCycleTime.display("0:00:00")
        
        self.chkStopNextCycle.clicked.connect(self.stopProduction)
        
        self.myThread = myThread(self)
        self.myThread.timeElapsed.connect(self.on_myThread_timeElapsed)
        self.myThread.finished.connect(self.on_myThread_finished)      
        
        sys.stdout = EmittingStream(textWritten=self.normalOutputWritten)
        
    def __del__(self):
        sys.stdout = sys.__stdout__
    
    def normalOutputWritten(self, text):
        if '!@#$' in text:
            self.tbLastRunLog.setText(text.replace('!@#$',''))
            self.myThread.resetTime()
        else:
            cursor = self.tbTerminalOut.textCursor()
            cursor.movePosition(QtGui.QTextCursor.End)
            cursor.insertText(text)
            self.tbTerminalOut.setTextCursor(cursor)
            self.tbTerminalOut.ensureCursorVisible()
    
    def openLog(self):
        startfile(logFile)  
    
    def stopProduction(self):
        runProd.stopProduction()
   
    @QtCore.pyqtSlot()
    def startProd(self):
        self.cmdStartProd.setText("Running...")
        self.myThread.start()
        
    @QtCore.pyqtSlot(int)
    def on_myThread_timeElapsed(self, seconds):
        self.lcdCycleTime.display(time.strftime("%H:%M:%S", time.gmtime(seconds)))  

    @QtCore.pyqtSlot()
    def on_myThread_finished(self):
        self.lcdCycleTime.display("0:00:00")
        self.tbTerminalOut.setText(r'')
        self.cmdStartProd.setText(r'Start Production')
        self.cmdStartProd.setChecked(False)
        self.chkStopNextCycle.setChecked(False)
      
if __name__ == "__main__":
    app = QtWidgets.QApplication.instance()
    if app is None:
        app = QtWidgets.QApplication(sys.argv)
    window = prodStatus()
    sys.exit(app.exec_())