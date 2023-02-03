"""
Author: Jeferson Coli - jcoli@tecnocoli.com.br
11/2018
Scanner for OBDII adapters using ELM327
Main Window
"""
import sys
from typing import Any, Union

import obd
from obd import Unit, OBDResponse
from obd import ECU
from obd.protocols.protocol import Message
from obd.utils import OBDStatus
from obd.OBDCommand import OBDCommand
from obd.decoders import noop

from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import QApplication, QMainWindow, QAction, QMessageBox, QFileDialog, QWidget, QGridLayout, \
    QLCDNumber
from PySide2.QtWidgets import QTextBrowser, QPushButton, QPlainTextEdit, QLCDNumber, QDial, QProgressBar, QDateTimeEdit, \
    QTimeEdit, QVBoxLayout, QTabWidget, QStatusBar
from PySide2.QtCore import QFile, QObject, QTime, QTimer, QDateTime
from PySide2.QtWidgets import QApplication, QMessageBox, QLabel
from PySide2.QtQuick import QQuickView
from PySide2.QtCore import QUrl
from PySide2.QtGui import QPixmap, QColor

from matplotlib.backends.backend_qt5agg import (
        FigureCanvas, NavigationToolbar2QT as NavigationToolbar)
from matplotlib.figure import Figure


import sqlite3

from datetime import datetime
from time import sleep

from functions.dataConnection import *
from functions.odbFunctions import *

import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# create a file handler
handler = logging.FileHandler('scanner.log')
handler.setLevel(logging.INFO)

# create a logging format
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

# add the handlers to the logger
logger.addHandler(handler)

logger.info('init')


obdConnect = False
#fig = Figure()
#ax = fig.add_subplot(1, 1, 1)
xs = []
ys = []
ys2 = []
ys3 = []
ys4 = []
d = 0.00
last_rpm = 0.00
last_speed = 0.00
last_cool_temp = 0.00
up_graph_en = False
scan_odb_en = False
flag_mil = False
redColor = QColor(255, 0, 0)
blackColor = QColor(0, 0, 0)


class Form(QMainWindow):
    xs = []
    ys = []
    ys2 = []
    ys3 = []
    ys4 = []
    d = 0.00
    last_rpm = 0.00
    last_speed = 0.00
    last_cool_temp = 0.00
    up_graph_en = False
    scan_odb_en = False
    obdConnect = False

    def __init__(self, ui_file, parent=None):
        super(Form, self).__init__(parent)
        ui_file = QFile(ui_file)
        ui_file.open(QFile.ReadOnly)

        loader = QUiLoader()
        loader.registerCustomWidget(GraphWidget)
        loader.registerCustomWidget(GraphWidget2)
        loader.registerCustomWidget(GraphWidget3)
        loader.registerCustomWidget(GraphWidget4)
        #loader.registerCustomWidget(GaugeRpmWidget)
        self.window = loader.load(ui_file)
        ui_file.close()
        self.btnConnect = self.window.findChild(QPushButton, 'ReconnectButton')
        self.btnConnect.clicked.connect(self.btnconnect_clicked)
        self.btnExit = self.window.findChild(QPushButton, 'btnExit')
        self.btnExit.clicked.connect(self.exit_clicked)

        self.btnTestOBd2 = self.window.findChild(QPushButton, 'btn_test_obd2')
        #self.btnTestOBd2.clicked.connect(self.test_odb2)
        self.btnTestOBd2.setText("Not Connect")
        self.btnTestOBd2.setEnabled(False)

        self.btnReadDTC = self.window.findChild(QPushButton, 'btnReadDtc')
        self.btnReadDTC.clicked.connect(self.reading_dtc_clicked)
        self.btnClearDTC = self.window.findChild(QPushButton, 'btnClearDtc')
        self.btnClearDTC.clicked.connect(self.clear_dtc_clicked)
        self.btnClearDTC.setEnabled(True)

        self.btnScanObd = self.window.findChild(QPushButton, 'btn_scan_odb')
        self.btnScanObd.clicked.connect(self.btnscanobd_clicked)
        self.btnScanObd.setEnabled(False)

        self.btnUpGraph = self.window.findChild(QPushButton, 'btn_up_graph')
        self.btnUpGraph.clicked.connect(self.btnupgraph_clicked)
        self.btnUpGraph.setEnabled(False)

        self.pText = self.window.findChild(QPlainTextEdit, 'plainTextEdit')
        self.pText.setReadOnly(True)
        self.pTextDtc = self.window.findChild(QPlainTextEdit, 'plainTextEdit_dtc')
        self.pTextDtc.setReadOnly(True)

        self.adDateTime = self.window.findChild(QDateTimeEdit, 'dateEdit')
        self.adDateTime.setDateTime(QDateTime.currentDateTime())
        self.adTime = self.window.findChild(QTimeEdit, 'timeEdit')
        self.adTime.setTime(QTime(QTime.currentTime()))
        self.lcd_time = self.window.findChild(QLCDNumber, 'lcdTime')
        self.lcd_rpm = self.window.findChild(QLCDNumber, 'lcdRpm')
        self.lcd_speed = self.window.findChild(QLCDNumber, 'lcdSpeed')
        self.lcd_CTemp = self.window.findChild(QLCDNumber, 'lcdCTemp')

        self.lbl_mil_on = self.window.findChild(QLabel, 'lbl_mil_on')
        self.lbl_mil_off = self.window.findChild(QLabel, 'lbl_mil_off')
        pixmap_mil_on = QPixmap('./images/mil-on.png')
        self.lbl_mil_on.setPixmap(pixmap_mil_on)
        pixmap_mil_off = QPixmap('./images/mil-off.png')
        self.lbl_mil_off.setPixmap(pixmap_mil_off)
        #self.lbl_mil_on.setEnabled(True)

        self.lbl_mil_off.hide()

        self.tab_bar = self.window.findChild(QTabWidget, 'tabWidget')
        self.tab_bar.setCurrentIndex(0);
        #self.tab_bar.blockSignals(True)  # just for not showing the initial message
        self.tab_bar.currentChanged.connect(self.onchange_tab)  # changed!

        self.status_bar= self.window.findChild(QWidget, 'status_bar')

        self.quick_Widget = self.window.findChild(QWidget, 'quickWidget')
        self.graphics_View = self.window.findChild(QWidget, 'graphicsView')

        self.widget_graph = self.window.findChild(QWidget, 'GraphWidget')
        self.widget_graph2 = self.window.findChild(QWidget, 'GraphWidget2')
        self.widget_graph3 = self.window.findChild(QWidget, 'GraphWidget3')
        self.widget_graph4 = self.window.findChild(QWidget, 'GraphWidget4')
        #self.widget_gauge_rpm = self.window.findChild(QQuickView, 'GaugeRpmWidget')

        grid_layout = QGridLayout()
        grid_layout.addWidget(self.window)
        self.setLayout(grid_layout)

        timerReadODB: object = QTimer(self)
        timerReadODB.timeout.connect(self.showTime)
        timerReadODB.start(3000)

        self.dataConnection = DataConnection("scanner-data.db")
        #self.dataConnection.close_db()

        self.functionObd = OdbFunctions()

        self.status_bar.showMessage('OBD-II adapter not Connect')

        self.window.show()

    def obd_connect(self):
        global obdConnect
        if not (self.functionObd.odb_scan_serial()) is None:
            if (self.functionObd.odb_scan_serial()) == 0:
                self.append_text_datetime('No OBD-II adapters found')
                self.status_bar.showMessage('No OBD-II adapters found')

                obdConnect = False
            else:
                logger.info('Connecting - main - obd_connect')
                lports = self.functionObd.odb_scan_serial()
                for nport in lports:
                    self.append_text_datetime('OBD2 scan port: ' + nport)
                try:
                    obd.logger.setLevel(obd.logging.DEBUG)
                    connect_car = self.functionObd.obd_connect()
                    logger.info('Connecting - main - obd_connect 1')
                    # connect_car = self.connection.is_connected()
                    logger.info(self.functionObd.support_command(obd.commands[1][0x0C]))
                    # logger.info(self.connection)
                    # self.connection = obd.OBD(protocol="8")
                    if self.functionObd.odb_status_elm():
                        self.append_text_datetime("Connect to the OBD-II adapter")
                        logger.info('Connect to the OBD-II adapter')
                        if connect_car:
                            obdConnect = True
                            self.btnConnect.setText("Reconnect")
                            self.btnTestOBd2.setEnabled(True)
                            self.btnClearDTC.setEnabled(True)
                            self.btnScanObd.setEnabled(True)
                            self.btnUpGraph.setEnabled(True)
                            self.btnClearDTC.setEnabled(True)
                            self.btnTestOBd2.setText("Test ODB2")
                            #self.append_text_datetime("Protocol: " + self.connection.protocol_name())
                            self.status_bar.setStyleSheet("background-color: rgb(162, 190, 255);")
                            if self.functionObd.odb_status_car:
                                self.append_text_datetime("Connected to the Car")
                                self.btnUpGraph.setEnabled(True)
                                self.btnScanObd.setEnabled(True)
                                self.btnClearDTC.setEnabled(True)
                                self.btnReadDTC.setEnabled(True)
                            else:
                                self.append_text_datetime("Not connected to the Car")
                            self.status_bar.showMessage('ELM OBD-II adapter Connected to the Car')
                        else:
                            self.status_bar.setStyleSheet("background-color: rgb(244, 255, 16);")
                            self.append_text_datetime('ELM OBD-II adapter not Connected to the Car')
                            self.status_bar.showMessage('ELM OBD-II adapter not Connected to the Car')
                            obdConnect = False
                except Exception as e:
                    self.append_text_datetime("Problem trying connecting OBD-II adapter")
                    self.append_text_datetime("Exception: " + str(e))
                finally:
                    self.append_text_datetime('End OBD2 Connection')
        else:
            self.append_text_datetime('No OBD-II adapters found')

    def closeEvent(self, event):

        #reply = QtGui.QMessageBox.question(self, 'Message', "Are you sure to quit?", QtGui.QMessageBox.Yes,
        #QtGui.QMessageBox.No)
        reply = QMessageBox
        reply.setIcon(QMessageBox.Information)
        msg.setWindowTitle("MessageBox demo")
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg.buttonClicked.connect(msgbtn)
        retval = msg.exec_()


        if reply == QtGui.QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

    def quit_app(self):
        # some actions to perform before actually quitting:
        QApplication.instance().quit
        ('CLEAN EXIT')

    def exit_clicked(self):
        box = QMessageBox()
        box.setWindowTitle('Are you sure?')
        box.setText("Exiting Application")
        box.setInformativeText("Are you sure to quit?")
        box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        box.setDefaultButton(QMessageBox.Save)
        reply = box.exec_()

        if reply == QMessageBox.Yes:
            #event.accept()
            self.window.close()
            print('CLEAN EXIT')
        else:
            #event.ignore()
            print('Exit Cancel')
        # some actions to perform before actually quitting:
        #QApplication.instance().quit
        #self.window.close()

    def clear_dtc_clicked(self):
        self.functionObd.clear_dtc()

    def reading_dtc_clicked(self):
        self.reading_dtc()

    def reading_dtc(self):
        global obdConnect

        try:
            if obdConnect:
                call_dtc = self.functionObd.reading_dtc()
                if not call_dtc.is_null():
                    for dtc in call_dtc.value:
                        self.append_text_dtc_datetime(dtc[0]+" - "+dtc[1])
        except Exception as e:
            self.append_text_datetime("Connection Error")

    def onchange_tab(self, i):
        global up_graph_en
        global scan_odb_en
        global xs
        global ys
        global ys2
        global ys3
        global ys4

        if i != 3:
            up_graph_en = False
            self.widget_graph.canvas.axes.clear()
            self.widget_graph2.canvas.axes.clear()
            self.widget_graph3.canvas.axes.clear()
            self.widget_graph4.canvas.axes.clear()
            self.widget_graph.canvas.draw()
            self.widget_graph2.canvas.draw()
            self.widget_graph3.canvas.draw()
            self.widget_graph4.canvas.draw()
            xs = []
            ys = []
            ys2 = []
            ys3 = []
            ys4 = []
            self.btnUpGraph.setText("Start Graph")
        if i != 0:
            scan_odb_en = False
            self.btnScanObd.setText("Start Scan")

    def btnscanobd_clicked(self):
        global scan_odb_en
        scan_odb_en = not scan_odb_en
        if scan_odb_en:
            self.btnScanObd.setText("Stop Scan")
        else:
            self.btnScanObd.setText("Start Scan")

    def btnupgraph_clicked(self):
        global up_graph_en
        up_graph_en = not up_graph_en
        if up_graph_en:
            self.btnUpGraph.setText("Stop Graph")
        else:
            self.btnUpGraph.setText("Start Graph")

    def update_graph(self):

        global xs
        global ys
        global ys2
        global ys3
        global ys4
        global obdConnect
        global up_graph_en
        global last_rpm
        global last_speed
        global last_cool_temp

        if up_graph_en:
            self.scan_odb2()
            xs.append(datetime.now().strftime('%S'))
            ys.append(last_rpm)
            ys2.append(last_speed)
            ys3.append(last_cool_temp)

            xs = xs[-50:]
            ys = ys[-50:]
            ys2 = ys2[-50:]
            ys3 = ys3[-50:]
            ys4 = ys4[-50:]

            self.widget_graph.canvas.axes.clear()
            self.widget_graph2.canvas.axes.clear()
            self.widget_graph3.canvas.axes.clear()
            self.widget_graph4.canvas.axes.clear()

            self.widget_graph.canvas.axes.grid()
            self.widget_graph2.canvas.axes.grid()
            self.widget_graph3.canvas.axes.grid()
            self.widget_graph4.canvas.axes.grid()

            self.widget_graph.canvas.axes.plot(xs, ys, color='tab:red')
            self.widget_graph2.canvas.axes.plot(xs, ys2, color='tab:green')
            self.widget_graph3.canvas.axes.plot(xs, ys3, color='tab:blue')

            for tick in self.widget_graph.canvas.axes.get_xticklabels():
                tick.set_rotation(75)
            for tick in self.widget_graph2.canvas.axes.get_xticklabels():
                tick.set_rotation(75)
            for tick in self.widget_graph3.canvas.axes.get_xticklabels():
                    tick.set_rotation(75)
            for tick in self.widget_graph4.canvas.axes.get_xticklabels():
                tick.set_rotation(75)

            self.widget_graph.canvas.axes.tick_params(axis='both', which='major', labelsize=5)
            self.widget_graph.canvas.axes.set_ylabel(r"RPM")
            self.widget_graph.canvas.axes.set_ylim(0, 8000)
            self.widget_graph2.canvas.axes.tick_params(axis='both', which='major', labelsize=5)
            self.widget_graph2.canvas.axes.set_ylabel(r"Speed")
            self.widget_graph2.canvas.axes.set_ylim(0, 220)
            self.widget_graph3.canvas.axes.tick_params(axis='both', which='major', labelsize=5)
            self.widget_graph3.canvas.axes.set_ylabel(r"Temperature")
            self.widget_graph3.canvas.axes.set_ylim(0, 150)
            self.widget_graph4.canvas.axes.tick_params(axis='both', which='major', labelsize=5)
            self.widget_graph4.canvas.axes.set_ylabel(r"Volts")
            self.widget_graph4.canvas.axes.set_ylim(0, 18)


            #self.widget_graph.canvas.axes1.autoscale_view(tight=None, scalex=True, scaley=False)
            #self.widget_graph.canvas.axes.plot(ys1)
            #self.widget_graph.canvas.axes1.set_ylabel(r"Speed")
            #self.widget_graph.canvas.axes1.set_ylim(0, 200)

            self.widget_graph.canvas.draw()
            self.widget_graph2.canvas.draw()
            self.widget_graph3.canvas.draw()
            self.widget_graph4.canvas.draw()

    def btnconnect_clicked(self):
        self.append_text_datetime('Connecting ELM OBD2 Adaptor....')
        self.status_bar.setStyleSheet("background-color: rgb(3, 255, 142);")
        self.status_bar.showMessage('Connecting.........')
        self.obd_connect()

    def append_text_datetime(self, pText):
        #self.pText.setTextColor(blackColor)
        self.pText.appendPlainText(
            datetime.now().strftime('%d-%m-%Y %H:%M:%S') + " --> " + pText)

    def append_text_datetime_color(self, pText, color):
        if color == "red":
            self.pText.setTextColor(redColor)
        else:
            self.pText.setTextColor(blackColor)

        self.pText.appendPlainText(
            datetime.now().strftime('%d-%m-%Y %H:%M:%S') + " --> " + pText)

    def append_text(self, pText):
        self.pText.appendPlainText(pText)

    def append_text_dtc_datetime(self, pText):
        self.pTextDtc.appendPlainText(
            datetime.now().strftime('%d-%m-%Y %H:%M:%S') + " --> " + pText)

    def append_text_dtc(self, pText):
        self.pTextDtc.appendPlainText(pText)

    def scan_odb2(self):
        global obdConnect
        global last_rpm
        global last_speed
        global last_cool_temp
        try:
            if obdConnect:
                call_rpm = self.functionObd.query_odb(obd.commands[1][0x0C])
                if not call_rpm.is_null():

                    rpm = call_rpm.value.magnitude
                    last_rpm = rpm
                call_cool_temp = self.functionObd.query_odb(obd.commands[1][0x05])
                if not call_cool_temp.is_null():
                    cool_temp = call_cool_temp.value.magnitude - 40
                    last_cool_temp = cool_temp
                call_speed = self.functionObd.query_odb(obd.commands[1][0x0D])
                if not call_speed.is_null():
                    speed = call_speed.value.magnitude
                    last_speed = speed
        except Exception as e:
            self.append_text_datetime("Connection Error")
            self.status_bar.showMessage('Connection Error')
            self.btnUpGraph.setEnabled(False)
            self.btnScanObd.setEnabled(False)
            self.btnClearDTC.setEnabled(False)
            self.btnReadDTC.setEnabled(False)
            obdConnect = False

    def showTime(self):
        global obdConnect
        global last_rpm
        global last_speed
        global last_cool_temp
        global scan_odb_en
        global up_graph_en
        global flag_mil

        time = QTime.currentTime()
        text = time.toString('hh:mm:ss')
        if (time.second() % 2) == 0:
            text = text[:2] + ' ' + text[3:]

        self.lcd_time.display(text)
        if flag_mil:
            self.lbl_mil_off.hide()
        else:
            self.lbl_mil_off.show()


        if up_graph_en:
            self.update_graph()

        if scan_odb_en:
            try:
                self.scan_odb2()
                if last_rpm > 6500:
                    self.lcd_rpm.setStyleSheet("background-color: rgb(102, 102, 102); color: rgb(249, 13, 88);")
                else:
                    self.lcd_rpm.setStyleSheet("background-color: rgb(102, 102, 102); color: rgb(174, 255, 242);")

                self.lcd_rpm.display(last_rpm)

                if last_cool_temp > 100:
                    self.lcd_CTemp.setStyleSheet("background-color: rgb(102, 102, 102); color: rgb(249, 13, 88);")
                else:
                    self.lcd_CTemp.setStyleSheet("background-color: rgb(102, 102, 102); color: rgb(174, 255, 242);")

                self.lcd_CTemp.display(last_cool_temp)

                if last_speed > 120:
                    self.lcd_speed.setStyleSheet("background-color: rgb(102, 102, 102); color: rgb(249, 13, 88);")
                else:
                    self.lcd_speed.setStyleSheet("background-color: rgb(102, 102, 102); color: rgb(174, 255, 242);")

                self.lcd_speed.display(last_speed)

            except Exception as e:
                self.append_text_datetime("Connection Error - Time")
                self.status_bar.showMessage('Connection Error - Time')
                obdConnect = False


class GraphWidget(QWidget):

    def __init__(self, parent=None):
        QWidget.__init__(self, parent)

        self.canvas = FigureCanvas(Figure())

        vertical_layout = QVBoxLayout()
        vertical_layout.addWidget(self.canvas)
        #vertical_layout.addWidget(NavigationToolbar(self.canvas, self))
        self.canvas.axes = self.canvas.figure.add_subplot(111)
        self.canvas.axes.grid()
        self.canvas.axes.autoscale_view(tight=None, scalex=True, scaley=False)
        for tick in self.canvas.axes.get_xticklabels():
            tick.set_rotation(75)
        self.setLayout(vertical_layout)


class GraphWidget2(QWidget):

    def __init__(self, parent=None):
        QWidget.__init__(self, parent)

        self.canvas = FigureCanvas(Figure())

        vertical_layout = QVBoxLayout()
        vertical_layout.addWidget(self.canvas)
        #vertical_layout.addWidget(NavigationToolbar(self.canvas, self))
        self.canvas.axes = self.canvas.figure.add_subplot(111)
        self.canvas.axes.grid()
        self.canvas.axes.autoscale_view(tight=None, scalex=True, scaley=False)
        for tick in self.canvas.axes.get_xticklabels():
            tick.set_rotation(75)
        self.setLayout(vertical_layout)


class GraphWidget3(QWidget):

    def __init__(self, parent=None):
        QWidget.__init__(self, parent)

        self.canvas = FigureCanvas(Figure())

        vertical_layout = QVBoxLayout()
        vertical_layout.addWidget(self.canvas)
        #vertical_layout.addWidget(NavigationToolbar(self.canvas, self))
        self.canvas.axes = self.canvas.figure.add_subplot(111)
        self.canvas.axes.grid()
        self.canvas.axes.autoscale_view(tight=None, scalex=True, scaley=False)
        for tick in self.canvas.axes.get_xticklabels():
            tick.set_rotation(75)
        self.setLayout(vertical_layout)


class GraphWidget4(QWidget):

    def __init__(self, parent=None):
        QWidget.__init__(self, parent)

        self.canvas = FigureCanvas(Figure())

        vertical_layout = QVBoxLayout()
        vertical_layout.addWidget(self.canvas)
        #vertical_layout.addWidget(NavigationToolbar(self.canvas, self))
        self.canvas.axes = self.canvas.figure.add_subplot(111)
        self.canvas.axes.grid()
        self.canvas.axes.autoscale_view(tight=None, scalex=True, scaley=False)
        for tick in self.canvas.axes.get_xticklabels():
            tick.set_rotation(75)
        self.setLayout(vertical_layout)


class GaugeRpmWidget(QQuickView):

    def __init__(self, parent=None):
        QQuickView.__init__(self, parent)
        view = QQuickView()
        url = QUrl("rpm.qml")

        view.setSource(url)
        view.show()


def main():
    app = QApplication(sys.argv)
    form = Form('forms/main-window.ui')

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()