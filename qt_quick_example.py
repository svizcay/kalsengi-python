import os, sys
os.environ['QT_API'] = 'pyside2'

from time import strftime, gmtime, localtime
from datetime import datetime

# from PyQt5.QtGui import QGuiApplication
# from PyQt5.QtQml import QQmlApplicationEngine

from qtpy.QtGui import QGuiApplication
from qtpy.QtQml import QQmlApplicationEngine
from qtpy.QtCore import QTimer

def update_time():
    # Pass the current time to QML.
    curr_time = strftime("%H:%M:%S", localtime())
    engine.rootObjects()[0].setProperty('currTime', curr_time)

if __name__ == "__main__":

    app = QGuiApplication(sys.argv)

    engine = QQmlApplicationEngine()
    engine.quit.connect(app.quit)
    engine.load('qt_quick_example.qml')

    timer = QTimer()
    timer.setInterval(100)  # msecs 100 = 1/10th sec
    timer.timeout.connect(update_time)
    timer.start()

    update_time() # initial startup

    sys.exit(app.exec_())
