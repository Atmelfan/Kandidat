import serial
import evdev
import time
import threading

ly, ry = 0, 0

class mdThread (threading.Thread):
    def __init__(self, ser):
        threading.Thread.__init__(self)
        self.ser = ser
        self.daemon = True

    def run(self):
        print("Starting " + self.ser.name)
        # Get lock to synchronize threads
        while True:
            ser.write(("ch1:vel %d; :ch2:vel %d" % (ry, ry)).encode())
            ser.readline()
            ser.flush()
            print("%f" % ry)
            time.sleep(0.25)


if __name__ == '__main__':
    #scan for DS4
    devices = [evdev.InputDevice(fn) for fn in evdev.list_devices()]
    ds4 = None
    for device in devices:
        if "sony" in device.name.lower():
            print("Found '%s'" % device.name)
            ds4 = device

    #Exit if not found
    if not ds4:
        print("Failed to find DS4 controller.")
        exit()

    print("Found DS4 controller!")
    ry = 0

    with serial.Serial('/dev/ttyACM0', 115200, timeout=0.1) as ser:
        #ser.write(b"\n\r")  # send command, ignore
        #ser.flush()
        #ser.readline()
        ser.write(b"*idn?\n\r")#send command, ignore
        ser.flush()
        #ser.readline()
        print("Motordriver: %s" % ser.readline())
        #mdThread(ser).start()
        try:
            for event in ds4.read_loop():
                if event.type == evdev.ecodes.EV_ABS and event.code == 5:
                    lry = int(event.value) - 127
                    lry *= (1800.0/127.0)
                    ser.write(("ch1:dir %s; vel %d\n\r" % ( "BACK" if lry > 0 else "FORW", abs(lry))).encode())
                    ser.flush()
                    #print("%.3f> %s" % (time.time(), ser.readline()))
                    #ser.readline()

                elif event.type == evdev.ecodes.EV_ABS and event.code == 1:
                    lly = int(event.value) - 127
                    lly *= (1800.0 / 127.0)
                    ser.write(("ch2:dir %s; vel %d\n\r" % ("BACK" if lly > 0 else "FORW", abs(lly))).encode())
                    ser.flush()
                    #print("%.3f> %s" % (time.time(), ser.readline()))
                    #ser.readline()

        except KeyboardInterrupt:
            ser.write(b"ch1:vel 0; :ch2:vel 0\n\r")









