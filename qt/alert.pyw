#! /usr/bin/ python

# handles cmd line args
import sys
# sleep function
import time
# pyqt funcs
from PyQt4.QtCore import *
from PyQt4.QtGui import *

app = QApplication(sys.argv)

# make sure we have the right args
try:
    due = QTime.currentTime()
    message = "Alert!"
    if len(sys.argv) < 2:
        raise ValueError
    hours, mins = sys.argv[1].split(":")
    due =  QTime(int(hours), int(mins))
    if not due.isValid():
        raise ValueError
    if len(sys.argv) > 2:
        message = " ".join(sys.argv[2:])

except ValueError:
    message = "Usage: alert.pyw HH:MM [optional message]"

# loop until we get the right time
while QTime.currentTime() < due:
    time.sleep(20)

# show the message
label = QLabel("<font color=red size=72><b>" + message + "</b></font>")
#label.setWindowFlags(Qt.SplashScreen)
label.show()
QTimer.singleShot(60000, app.quit)
app.exec_()
