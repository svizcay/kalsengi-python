from engine import Window, Triangle

# notes regarding qt for python
# pyQt developed by 3rd party company. license is GPL (more restrictive than LGPL)
# pySide is the official binding but it was lagging behind (no so much now). License is LGPL (less restrictive).
# qtpy is an abstraction to work with any of them

# # import qtpy
# import os, sys
# this is a technique for setting env variables from code
# os.environ['QT_API'] = 'pyside2'
# from qtpy import QtWidgets
# using Pyside2 directly (no qtpy)
#import PySide2.QtCore

if __name__ == "__main__":

    window = Window(1024, 768, "Example App")

    window.run()
    print("closing application")
