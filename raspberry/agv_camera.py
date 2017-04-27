from threading import Thread

import numpy as np
import cv2
import cv2.aruco as aruco
import time
import math
import picamera
from picamera.array import PiRGBArray




aruco_dict = aruco.Dictionary_get(aruco.DICT_6X6_250)
parameters = aruco.DetectorParameters_create()

ARUCO_TAG_HEIGHT = 25
ARUCO_TAG_WIDTH = 25

# Focal length = (Pixels x Distance) / Size
RASPICAM_FOCAL_LENGTH = 1
POTATO_FOCAL_LENGTH = 1


class AGVCamera(Thread):
    resolution = 0,0

    def __init__(self, resolution=(720, 480)):
        super(AGVCamera, self).__init__(daemon=True)
        self.resolution = resolution

    def run(self):
        with picamera.PiCamera(sensor_mode=5, resolution=(1640, 922), framerate=2) as camera:
            print("Actual resolution: %s@mode=%d, framerate=%d" % (
            str(camera.resolution), camera.sensor_mode, camera.framerate))

            time.sleep(0.5)
            rawCapture = PiRGBArray(camera)
            rawCapture.truncate(0)
            # camera.start_preview()
            t = time.time()
            a = False
            n = 1
            tot = 0
            try:
                for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True, resize=(720,480)):
                    s = time.time()
                    cvimage = frame.array
                    # cvimaget = cv2.resize(cvimage, None, fx=args.resize, fy=args.resize)
                    # cvimaget = cv2.cvtColor(cvimaget, cv2.COLOR_BGR2GRAY) # no performance gain
                    aruco_tags = detect_and_cal_tags(cvimage, RASPICAM_FOCAL_LENGTH)
                    rawCapture.truncate(0)
                    t1 = time.time()
                    tot = tot + (t1 - t)
                    if not a:
                        cv2.imwrite('t.jpg', cvimage)
                        cv2.imwrite('tt.jpg', cvimaget)

                        a = True
                    print("dt=%s, at = %f, pt = %f, %s" % (t1 - t, tot / n, t1 - s, aruco_tags))
                    t = t1
                    n = n + 1


            except KeyboardInterrupt:
                pass
            finally:
                # camera.stop_preview()
                pass
        pass
