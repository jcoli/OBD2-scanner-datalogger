# Class OdbService:
# list services OBDII

from dataclasses import dataclass


@dataclass
class OdbService:

    id: long
    description_eng: string
    description_por: string
    description_esp: string

