import time
from enum import Enum

from agv_camera import AGVCamera
from agv_linefollow import LineMode
from bluetooth_server import BluetoothServer
from scpi_server import ScpiCommandInline, ScpiServer

from agv_sensors import AGVSensors
from scpi_client import ScpiClient
from states.agv_state import *

datastore = {
    "drop": 0,
    "station": -1,
    "passengers": 0,
    "max_passengers": 10,
    "start": False
}
state = AGVStateStop(datastore)


class AGVRole:
    LEADER = 0
    FOLLOWER = 1

role = AGVRole.FOLLOWER

# NAVigate:STARt
def set_start(args):
    global state
    state = AGVStateStart(datastore)
    return "STARTED!"

# NAVigate:STOp
def set_stop(args):
    global state
    state = AGVStateStop(datastore)
    return "STOPPED!"

# NAVigate:STATus
def query_status(args):
    return state.log()


# NAVigate:PICKup
def set_pickup(args):
    if len(args) != 2:
        return "ERR: Expected 2 arguments, got %s" % len(args)
    try:
        station = int(args[0])
        drop = -int(args[1])

    except ValueError:
        return "ERR: Not a number"

    datastore['station'] = station
    datastore['drop'] = drop

    return query_pickup([])


def query_pickup(args):
    (station, drop) = datastore['station'], datastore['drop']
    return "%d %d" % (station, -drop if drop < 0 else 0)


# NAVigate:DROPoff
def set_dropoff(args):
    if len(args) != 2:
        return "ERR: Expected 2 arguments, got %s" % len(args)
    try:
        station = int(args[0])
        drop = int(args[1])

    except ValueError:
        return "ERR: Not a number"
    datastore['station'] = station
    datastore['drop'] = drop
    return query_dropoff([])


def query_dropoff(args):
    (station, drop) = datastore['station'], datastore['drop']
    return "%d %d" % (station, drop if drop > 0 else 0)


# NAVigate:ROLe
def set_role(args):
    if len(args) != 1:
        return "ERR: Expected 1 arguments, got %s" % len(args)
    rol = args[0].lower()
    if rol in ("lead", "leader"):
        role = AGVRole.LEADER
    else:
        role = AGVRole.FOLLOWER
    return query_role([])


def query_role(args):
    return "%s" % role


# NAVigate:PASSengers
def set_passengers(args):
    if len(args) != 1:
        return "ERR: Expected 1 arguments, got %s" % len(args)
    try:
        maximum = int(args[0])

    except ValueError:
        return "ERR: Not a number %s" % args[0]
    datastore['max_passengers'] = maximum
    return "%d" % maximum


def query_passengers(args):
    passengers = datastore['passengers']
    return "%d" % passengers

# Init SCPI commands
cmds = {
    "NAVigate:STATus": ScpiCommandInline(read=query_status),
    "NAVigate:STARt": ScpiCommandInline(write=set_start),
    "NAVigate:STOp": ScpiCommandInline(write=set_stop),
    "NAVigate:PICKup": ScpiCommandInline(write=set_pickup, read=query_pickup),
    "NAVigate:DROPoff": ScpiCommandInline(write=set_dropoff, read=set_dropoff),
    "NAVigate:PASSengers": ScpiCommandInline(write=set_passengers, read=query_passengers),

    "*IDN": ScpiCommandInline(write=lambda args: None, read=lambda args: "AGV-3 0.1.1")
}

if __name__ == '__main__':
    # Init modules
    server = ScpiServer(cmds)
    bluetooth = BluetoothServer("AGV-3", server)
    sensors = AGVSensors()
    motors = ScpiClient("/dev/ttyACM0")
    mode = LineMode.DISABLE
    cameras = AGVCamera()
    time.sleep(1)

    # Start main loop
    print("[MAIN] Starting main loop...")
    P = 500

    state.start() # initialize start state
    try:
        while True:
            #print("%s %d || %s %d" % (sensors.get_line(), sensors.get_rline(), sensors.get_line()[::-1], sensors.get_lline()))
            #try:
            next_state = state.update(cameras.get_tags(), sensors.get_line())
            if next_state:
                print("Switching state from [%s] to [%s]!" % (state.get_name(), next_state.get_name()))
                state.stop()#clean stop of last state
                state = next_state #switch state
                state.start()#initialize new state
            mode = state.line_mode()
            #print("%s" % mode.name)

            #except Exception as e:
            #    print("Unexpected error during state update: %s" % e)

            i = sensors.get_rline() if mode == LineMode.KEEP_RIGHT else sensors.get_lline()
            if mode == LineMode.KEEP_STRAIGHT:
                motors.send(("ch1:dir %s; vel %d\n\r" % ("BACK", 500)).encode(), 0)
                motors.send(("ch2:dir %s; vel %d\n\r" % ("BACK", 500)).encode(), 0)
            elif i == -1 or mode == LineMode.DISABLE:
                motors.send(("ch1:dir %s; vel %d\n\r" % ("BACK", 0)).encode(), 0)
                motors.send(("ch2:dir %s; vel %d\n\r" % ("BACK", 0)).encode(), 0)
            elif i >= 4:
                react = (i - 4 + 1)*P
                lly = 1500-react
                rly = 1500
                motors.send(("ch1:dir %s; vel %d\n\r" % ("BACK" if lly > 0 else "FORW", abs(lly))).encode(),0)
                motors.send(("ch2:dir %s; vel %d\n\r" % ("BACK" if rly > 0 else "FORW", abs(rly))).encode(), 0)
            else:
                react = (3 - i + 1)*P
                lly = 1500 - react
                rly = 1500
                motors.send(("ch2:dir %s; vel %d\n\r" % ("BACK" if lly > 0 else "FORW", abs(lly))).encode(), 0)
                motors.send(("ch1:dir %s; vel %d\n\r" % ("BACK" if rly > 0 else "FORW", abs(rly))).encode(), 0)
            #print("!2")
            time.sleep(0.05)
    except KeyboardInterrupt as e:
        pass
    finally:
        motors.send(("ch1:dir %s; vel %d\n\r" % ("FORW", 0)).encode(), 0)
        motors.send(("ch2:dir %s; vel %d\n\r" % ("FORW", 0)).encode(), 0)





