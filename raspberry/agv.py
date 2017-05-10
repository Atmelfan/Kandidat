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
    "station": 0,
    "passengers": 0,
    "max_passengers": 10,
    "lead": False,
    "start": False
}
state = AGVStateStop(datastore)
P = 90
I = 0.135
D = 90
BASE_SPEED = 1500
BASE_DISTANCE = 10.0

class AGVRole:
    LEADER = 0
    FOLLOWER = 1

role = AGVRole.FOLLOWER


# NAVigate:STARt
def set_start(args):
    global state
    state = AGVStateStart(datastore)
    return "STARTED!"


# SYStem:VELocity
def set_vel(args):
    global BASE_SPEED
    if len(args) != 1:
        return "ERR: Expected 1 arguments, got %s" % len(args)
    try:
        BASE_SPEED = int(args[0])
    except ValueError:
        return "ERR: Not a number!"
    return "%s" % BASE_SPEED


# SYStem:P
def set_p(args):
    global P
    if len(args) != 1:
        return "ERR: Expected 1 arguments, got %s" % len(args)
    try:
        P = int(args[0])
    except ValueError:
        return "ERR: Not a number!"
    return "%s" % P


# SYStem:I
def set_i(args):
    global I
    if len(args) != 1:
        return "ERR: Expected 1 arguments, got %s" % len(args)
    try:
        I = float(args[0])
    except ValueError:
        return "ERR: Not a number!"
    return "%s" % I


# SYStem:D
def set_d(args):
    global D
    if len(args) != 1:
        return "ERR: Expected 1 arguments, got %s" % len(args)
    try:
        D = float(args[0])
    except ValueError:
        return "ERR: Not a number!"
    return "%s" % D


# NAVigate:STOp
def set_stop(args):
    global state
    state = AGVStateStop(datastore)
    if len(args) == 1 && args[0] == 'hammertime':
        return "STOPPED! HAMMER TIME!"

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
    global datastore
    global state
    if len(args) != 1:
        return "ERR: Expected 1 arguments, got %s" % len(args)
    rol = args[0].lower()
    if rol in ("lead", "leader"):
        datastore['lead'] = True
        if type(state) == AGVStateStationExit:
            state = AGVStateFollow(datastore)
    elif rol in ("follow", "follower"):
        datastore['lead'] = False
        if type(state) == AGVStateStationExit:
            state = AGVStateFollow(datastore)
    else:
        return "ERR: Not a valid role %s" % rol
    return query_role([])


def query_role(args):
    return "LEAD" if datastore['lead'] else "FOLLOW"


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
    "NAVigate:ROLe": ScpiCommandInline(write=set_role, read=query_role),
    "NAVigate:PICKup": ScpiCommandInline(write=set_pickup, read=query_pickup),
    "NAVigate:DROPoff": ScpiCommandInline(write=set_dropoff, read=query_dropoff),
    "NAVigate:PASSengers": ScpiCommandInline(write=set_passengers, read=query_passengers),

    "SYStem:VELocity": ScpiCommandInline(write=set_vel),
    "SYStem:P": ScpiCommandInline(write=set_p),
    "SYStem:I": ScpiCommandInline(write=set_i),
    "SYStem:D": ScpiCommandInline(write=set_d),

    "*IDN": ScpiCommandInline(write=lambda args: None, read=lambda args: "AGV-3 0.1.1")
}

if __name__ == '__main__':
    # Init modules
    server = ScpiServer(cmds)
    bluetooth = BluetoothServer("AGV-3", server)
    sensors = AGVSensors()
    motors = ScpiClient("/dev/ttyACM0", baudrate=230400)
    mode = LineMode.DISABLE
    cameras = AGVCamera()
    time.sleep(1)
    integral = 0
    last_i = 0
    print("[MAIN] Battery voltage: %f V" % sensors.get_battery())

    # Start main loop
    dist_integral = 0.0
    print("[MAIN] Starting main loop...")

    state.start() # initialize start state
    try:
        while True:
            #print("%s %d || %s %d" % (sensors.get_line(), sensors.get_rline(), sensors.get_line()[::-1], sensors.get_lline()))
            #try:
            next_state = state.update(cameras.get_tags(), sensors.get_lastline())
            if next_state:
                print("Switching state from [%s] to [%s]!" % (state.get_name(), next_state.get_name()))
                state.stop()#clean stop of last state
                state = next_state #switch state
                state.start()#initialize new state
            mode = state.line_mode()
            #print("%s" % mode.name)
            reverse = False
            #except Exception as e:
            #    print("Unexpected error during state update: %s" % e)
            dist = sensors.get_distance()
            speed_mod = 1.0
            if dist < 15.0:
                dist_error = (dist - 12.50)
                if dist_error < 0.0 and dist_integral > -10:
                    dist_integral += dist_error

                speed_mod += dist_error*0.2 + dist_integral*0.05

                if speed_mod < 0:
                    #reverse = True
                    speed_mod *= 0.5

            speed_mod *= state.speed_factor()
            if speed_mod < 0.75:
                p = 150
                int_ = 0.1
                d = 90
            else:
                p = P
                int_ = I
                d = D


            i = sensors.get_rline() if mode == LineMode.KEEP_RIGHT else sensors.get_lline()
            if mode == LineMode.KEEP_STRAIGHT:
                motors.send(("ch1:dir %s; vel %d\n\r" % ("BACK", 500)).encode(), 0)
                motors.send(("ch2:dir %s; vel %d\n\r" % ("BACK", 500)).encode(), 0)
            elif i == -1 or mode == LineMode.DISABLE:
                motors.send(("ch1:dir %s; vel %d\n\r" % ("BACK", 0)).encode(), 0)
                motors.send(("ch2:dir %s; vel %d\n\r" % ("BACK", 0)).encode(), 0)
            elif i >= 4:
                if i < BASE_SPEED/2:
                    i += (i - 4 + 1)
                react = (i - 4 + 1)*p + int_*p + ((i - 4 + 1) - last_i)*d
                last_i = (i - 4 + 1)
                lly = BASE_SPEED - (react if not reverse else 0)
                lly *= speed_mod
                rly = BASE_SPEED - (react if reverse else 0)
                rly *= speed_mod
                motors.send(("ch1:dir %s; vel %d\n\r" % ("BACK" if lly > 0 else "FORW", abs(lly))).encode(),0)
                motors.send(("ch2:dir %s; vel %d\n\r" % ("BACK" if rly > 0 else "FORW", abs(rly))).encode(), 0)
            else:
                if i < BASE_SPEED/2:
                    i -= (3 - i + 1)
                react = (3 - i + 1)*p - i*int_ + ((3 - i + 1) - last_i)*d
                last_i = (3 - i + 1)
                lly = BASE_SPEED - (react if not reverse else 0)
                lly *= speed_mod
                rly = BASE_SPEED - (react if reverse else 0)
                rly *= speed_mod
                motors.send(("ch2:dir %s; vel %d\n\r" % ("BACK" if lly > 0 else "FORW", abs(lly))).encode(), 0)
                motors.send(("ch1:dir %s; vel %d\n\r" % ("BACK" if rly > 0 else "FORW", abs(rly))).encode(), 0)
            #print("!2")
            time.sleep(0.02)
    except KeyboardInterrupt as e:
        pass
    finally:
        motors.send(("ch1:dir %s; vel %d\n\r" % ("FORW", 0)).encode(), 0)
        motors.send(("ch2:dir %s; vel %d\n\r" % ("FORW", 0)).encode(), 0)





