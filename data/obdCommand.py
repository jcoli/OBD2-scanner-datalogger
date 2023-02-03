from dataclasses import dataclass


@dataclass
class OdbMsg:
    id: long
    mode: int
    name_eng: string
    name_por: string
    name_esp: string
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
    decoder: int
    ECU: int
    fast: bool



    def save_1(self, mode: int,  pid_hex: string, pid_dec: int, description_eng: string,
               description_por: string):
        self.mode = mode
        self.pid_hex = pid_hex
        self.pid_dec = pid_dec
        self.description_eng = description_eng
        self.description_por = description_por

