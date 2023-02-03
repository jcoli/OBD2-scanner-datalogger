"""
Author: Jeferson Coli - jcoli@tecnocoli.com.br
11/2018
Scanner for OBDII adapters using ELM327
Stored Database
"""

import sqlite3

from datetime import datetime

import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.FileHandler('scanner.log')
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


class DataConnection(object):

    def __init__(self, db_name):

        logger.info('Data Connection Init')

        try:
            self.conn = sqlite3.connect(db_name)
            self.cur = self.conn.cursor()
            print("Database: ", db_name)
            self.cur.execute('SELECT SQLITE_VERSION()')
            self.data = self.cur.fetchone()
            print("SQLite version: %s" % self.data)
        except sqlite3.Error:
            print("Error Open Database")
            return False

    def close_db(self):
        try:
            if self.conn:
                self.conn.close()
                logger.info('Connection closed')

            else:
                logger.info("No connection.")
        except sqlite3.Error:
            logger.info("Error Close Database")
            return False

    def list_dtc_error(self, pid):
        print("list DTC error")
        logger.info("list DTC error")

    def find_dtc_error(self, pid):
        print("find DTC error")
        logger.info("find DTC error")

    def list_standard_pid(self, pid):
        print("list Standard PID")
        logger.info("list Standard PID")

    def search_standard_pid(self, pid):
        print("list Standard PID")
        logger.info("list Standard PID")

    def search_command_mode1(self, pid):
        print("find command mode 1")
        logger.info("find command mode 1")

    def search_command_mode2(self, pid):
        print("find command mode 2")
        logger.info("find command mode 2")

    def search_command_mode3(self, pid):
        print("find command mode 3")
        logger.info("find command mode 3")

    def search_command_mode4(self, pid):
        print("find command mode 4")
        logger.info("find command mode 4")

    def search_command_mode5(self, pid):
        print("find command mode 5")
        logger.info("find command mode 5")

    def search_command_mode6(self, pid):
        print("find command mode 6")
        logger.info("find command mode 6")

    def search_command_mode7(self, pid):
        print("find command mode 7")
        logger.info("find command mode 7")

    def search_command_mode8(self, pid):
        print("find command mode 8")
        logger.info("find command mode 8")

    def search_command_mode9(self, pid):
        print("find command mode 9")
        logger.info("find command mode 9")
