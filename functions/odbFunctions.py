"""
Author: Jeferson Coli - jcoli@tecnocoli.com.br
11/2018
Scanner for OBDII adapters using ELM327
Obd call functions
"""

import obd
from obd import Unit, OBDResponse
from obd import ECU
from obd.protocols.protocol import Message
from obd.utils import OBDStatus
from obd.OBDCommand import OBDCommand
from obd.decoders import noop
import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.FileHandler('scanner.log')
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)




class OdbFunctions(object):
    obdConnect = False

    def __init__(self):
        #self.connection = self.obd_connect()
        logger.info('Odb_Functions Init')
        print("aqui connect")

    def odb_scan_serial(self):
        if len(obd.scan_serial()) == 0:
            return 0
        else:
            lports = obd.scan_serial()
            print(lports)
            return lports

    def odb_status_elm(self):
        return OBDStatus.ELM_CONNECTED

    def odb_status_car(self):
        return OBDStatus.CAR_CONNECTED

    def support_command(self, cmd):
        print("support ", cmd)
        return self.connection.supports(cmd)

    # Function to connect to OBDII adapter
    def obd_connect(self):
        global obdConnect
        if len(obd.scan_serial()) == 0:
            obdConnect = False
        else:
            lports = obd.scan_serial()
            print(lports)
            try:
                #obd.logger.setLevel(obd.logging.DEBUG)
                self.connection = obd.OBD()
                connect_car = self.connection.is_connected()
                # self.connection = obd.OBD(protocol="8")
                logger.info('Connect')
                logger.info(obd.commands[1][0x0C])
                logger.info(self.connection.is_connected())
                logger.info(self.connection.status())
                logger.info(self.connection.protocol_name())
                if OBDStatus.ELM_CONNECTED:
                    if connect_car:
                        logger.info('Connect 1')
                        obdConnect = True
                        if OBDStatus.CAR_CONNECTED:
                            print("Connected to the Car")
                            logger.info('Connect 2')
                            return True
                        else:
                            print("Not connected to the Car")
                            logger.info('Connect 2a')
                            return False

                    else:
                        obdConnect = False
                        logger.info('Connect 3')
            except Exception as e:
                        print("Problem trying connecting OBD-II adapter")
                        print("Exception: " + str(e))
            finally:
                        print('End OBD2 Connection')
            return self.connection

    def query_odb(self, cmd):
        return self.connection.query(cmd)

    def clear_dtc(self):
        global obdConnect
        try:
            if obdConnect:
                self.connection.query(obd.commands.CLEAR_DTC)
        except Exception as e:
            print('Connection Error: ', e)

    def reading_dtc(self):
        global obdConnect
        try:
            if obdConnect:
                #call_dtc = self.connection.query(obd.commands.GET_DTC)
                call_dtc = self.connection.query(obd.commands[3][1])
                if not call_dtc.is_null():
                    return call_dtc
        except Exception as e:
            print("Connection Error ", e)
