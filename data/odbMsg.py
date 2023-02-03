# Class odbMsg
# structure dor odbII msgs

from dataclasses import dataclass


@dataclass
class OdbMsg:

    id: long
    service: int
    dtc: bool
    pid_hex: string
    pid_dec: int
    byte_ret: int
    description_eng: string
    description_por: string
    description_esp: string
    min_value: float
    max_value: float
    unit: int
    formula: string
    valueA: float
    valueB: float
    value: float
    


    def save_1(self, service: int, dtc: bool, pid_hex: string, pid_dec: int, description_eng: string,
               description_por: string):
        self.service = service
        self.dtc = dtc
        self.pid_hex = pid_hex
        self.pid_dec = pid_dec
        self.description_eng = description_eng
        self.description_por = description_por
