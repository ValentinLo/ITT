#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import csv
from random import shuffle
from time import strftime
import itertools
from PyQt4 import QtGui, QtCore

"""
This Script runs a test on Fitts Law and creates a CSV with log results
It takes a textfile as argument with the information of the size and distance
of the targets and the age, gender and number of the user
"""


class ClickRecorder(QtGui.QWidget):

    def __init__(self):
        super(ClickRecorder, self).__init__()
        self.counter = 0
        self.user = None
        self.age = 0
        self.gender = None
        self.combinations = []
        self.time_counting = QtCore.QTime()
        self.moving = False
        self.log = {}
        self.target = None
        self.current_mouse_pos = None
        self.initUI()

    def initUI(self):
        self.showFullScreen()
        self.setWindowTitle('Fitts Law')
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.show()

    def mousePressEvent(self, ev):
        """
        Handles the click events.
        Keeps track of counter, updates the log, catches current timestamp and
        target position
        Creates CSV after last target and exits program
        """
        # is left click mouse and inside of the ellipse
        if ev.buttons() == QtCore.Qt.LeftButton:
            if self.target.contains(ev.pos()):

                # show next target if not finished
                if self.counter <= len(self.combinations):
                    timestamp = strftime("%Y-%m-%d %H:%M:%S")
                    duration = self.time_counting.elapsed()
                    click_position = ev.globalPos()
                    self.createlog(timestamp, duration, click_position)
                    self.moving = False
                    self.current_mouse_pos = None
                    self.counter += 1
                    self.update()
                    if self.counter == 16:  # exit program after last target
                        self.createCSV()
                        sys.exit()

    def eventFilter(self, source, ev):
        """
        Detects the mouse movement and starts counter after the first movement
        """
        if ev.type() == QtCore.QEvent.MouseMove:
            if ev.buttons() == QtCore.Qt.NoButton:
                if self.moving is False:
                    self.moving = True
                    self.time_counting.start()
            self.update()
        return QtGui.QMainWindow.eventFilter(self, source, ev)

    def createlog(self, timestamp, duration, click_position):
        """
        Updates Dict with all Information of clicked Target
        Prints Dict keys and current content to stdout
        """
        width = self.combinations[self.counter][1]
        distance = self.combinations[self.counter][0]
        self.log[self.counter] = {"Timestamp(ISO)": timestamp}
        self.log[self.counter]["UserID"] = self.user
        self.log[self.counter]["Trial"] = self.counter + 1
        self.log[self.counter]["Time(ms)"] = duration
        self.log[self.counter]["Gender(m/w)"] = self.gender
        self.log[self.counter]["Age"] = self.age
        self.log[self.counter]["Target_width"] = width
        self.log[self.counter]["Target_distance"] = distance
        self.log[self.counter]["Click_PosX"] = click_position.x()
        self.log[self.counter]["Click_PosY"] = click_position.y()
        self.log[self.counter]["Mouse_PosX"] = self.current_mouse_pos.x()
        self.log[self.counter]["Mouse_PosY"] = self.current_mouse_pos.y()
        self.log[self.counter]["Target_PosX"] = self.target.x()
        self.log[self.counter]["Target_PosY"] = self.target.y()
        if self.counter == 0:
            print self.log[self.counter].keys()
        print self.log[self.counter].values()

    def paintEvent(self, event):
        """
        paintEvent is triggerd after every update
        Updates text and target
        """
        qp = QtGui.QPainter()
        qp.begin(self)
        self.drawText(event, qp)
        self.drawTarget(event, qp)
        qp.end()

    def drawText(self, event, qp):
        """
        Updates textfield with counting time and number of targets
        """
        qp.setPen(QtGui.QColor(168, 34, 3))
        qp.setFont(QtGui.QFont('Decorative', 32))
        trial = str(self.counter + 1)
        len_com = len(self.combinations)
        time_el = str(self.time_counting.elapsed())
        self.text = "%s / %s (%s ms)" % (trial, len_com, time_el)
        qp.drawText(event.rect(), QtCore.Qt.AlignCenter + 200, self.text)

    def drawTarget(self, event, qp):
        """
        Draws circle targets with current distance and width
        Resets and logs mouse position with ever new target
        """
        if self.counter < len(self.combinations):
            width = self.combinations[self.counter][1]
            distance = self.combinations[self.counter][0]
            distance -= width/2.0  # distance to center of target
            size = self.geometry()
            circle = QtCore.QRect(distance, size.height()/2, width, width)
            if self.current_mouse_pos is None:  # get mouse pos
                cursor = QtGui.QCursor()
                cursor.setPos(0, (size.height()/2) + (width/2))
                self.current_mouse_pos = QtGui.QCursor.pos()
            qp.setBrush(QtGui.QColor(200, 34, 34))
            self.target = circle
            qp.setRenderHint(QtGui.QPainter.Antialiasing)
            qp.drawEllipse(circle)

    def readInput(self):
        """
        Parses textfile passed as argument
        If no file passed, program is exited
        """
        if len(sys.argv) > 1:  # check if textfile is passed as argument
            with open(sys.argv[1]) as fp:
                testsite_array = fp.readlines()
            user_raw = map(str, testsite_array[0].split())
            width_raw = map(str, testsite_array[1].split())
            distance_raw = map(str, testsite_array[2].split())
            age_raw = map(str, testsite_array[3].split())
            gender_raw = map(str, testsite_array[4].split())

            user_raw = map(int, user_raw[1].split(","))
            self.user = user_raw[0]
            width = map(int, width_raw[1].split(","))
            self.age = int(age_raw[1])
            self.gender = gender_raw[1]
            distance = map(int, distance_raw[1].split(","))
            self.combinations = 4 * list(itertools.product(distance, width))
            shuffle(self.combinations)
        else:  # else exit the program
            print("Please pass a textfile as argument")
            sys.exit()

    def createCSV(self):
        """
        Creates CSV file out of gatherd logs of Dict
        """
        lfile = open("User_%s" % self.user + ".csv", 'wb')
        keys = self.log[2].keys()
        out = csv.DictWriter(lfile, keys, delimiter=';', quoting=csv.QUOTE_ALL)
        out.writeheader()

        for key in self.log.keys():
            # print self.log[key]  # prints out whole logfile
            out.writerow(self.log[key])

        lfile.close()


def main():
    app = QtGui.QApplication(sys.argv)
    click = ClickRecorder()
    click.readInput()
    app.installEventFilter(click)
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
