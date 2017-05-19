from enum import Enum


class AGVSigns(Enum):
    TYPE_GLOBAL = 0x00
    TYPE_CUSTOM_AGV1 = 0x10
    TYPE_CUSTOM_AGV2 = 0x20
    TYPE_CUSTOM_AGV3 = 0x30
    TYPE_CUSTOM_AGV4 = 0x40
    TYPE_CUSTOM_AGV5 = 0x50
    TYPE_CUSTOM_AGV6 = 0x60

    TYPE_STATION_ENTER = 0xA0
    TYPE_STATION_STOP = 0xD0
    TYPE_STATION_EXIT = 0xE0

    TYPE_REGISTRATION = 0xB0
    TYPE_UNKNOWN = 0xF0

    @staticmethod
    def get_type(sign):
        return {
            0x00: AGVSigns.TYPE_GLOBAL,
            0x10: AGVSigns.TYPE_CUSTOM_AGV1,
            0x20: AGVSigns.TYPE_CUSTOM_AGV2,
            0x30: AGVSigns.TYPE_CUSTOM_AGV3,
            0x40: AGVSigns.TYPE_CUSTOM_AGV4,
            0x50: AGVSigns.TYPE_CUSTOM_AGV5,
            0x60: AGVSigns.TYPE_CUSTOM_AGV6,
            0xA0: AGVSigns.TYPE_STATION_ENTER,
            0xB0: AGVSigns.TYPE_REGISTRATION,
            0xD0: AGVSigns.TYPE_STATION_STOP,
            0xE0: AGVSigns.TYPE_STATION_EXIT
        }.get(sign & 0xF0, AGVSigns.TYPE_UNKNOWN)

    @staticmethod
    def make_id(type, id):
        return (type.value & 0xF0) | (id & 0x0F)










