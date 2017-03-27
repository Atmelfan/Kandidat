import argparse

import numpy as np
import cv2
import cv2.aruco as aruco
import time
import math


aruco_dict = aruco.Dictionary_get(aruco.DICT_6X6_250)
parameters = aruco.DetectorParameters_create()

ARUCO_TAG_HEIGHT = 25
ARUCO_TAG_WIDTH = 25

# Focal length = (Pixels x Distance) / Size
WEBCAM_FOCAL_LENGTH = 1
RASPICAM_FOCAL_LENGTH = 1
POTATO_FOCAL_LENGTH = 1


#
#
def get_distance(height, fl):
    return (ARUCO_TAG_HEIGHT * fl) / height


# find_middle(tag_corners)
#
def find_middle(tag_corners):
    maxx, maxy = max(tag_corners[0][0], tag_corners[1][0], tag_corners[2][0], tag_corners[3][0]), \
                 max(tag_corners[0][1], tag_corners[1][1], tag_corners[2][1], tag_corners[3][1])

    minx, miny = min(tag_corners[0][0], tag_corners[1][0], tag_corners[2][0], tag_corners[3][0]), \
                 min(tag_corners[0][1], tag_corners[1][1], tag_corners[2][1], tag_corners[3][1])
    return (maxx + minx) / 2, (maxy + miny) / 2, maxx - minx, maxy - miny


# detect_and_cal_tags(a_image, overlay)
#
def detect_and_cal_tags(a_image, focal_length=WEBCAM_FOCAL_LENGTH):
    corners, ids, rejected_points = aruco.detectMarkers(a_image, aruco_dict, parameters=parameters)
    tags = []
    if ids is not None:
        for x in range(0, len(ids)):
            xid = ids[x][0]
            # print(corners[x][0])
            xx, xy, w, h = find_middle(corners[x][0])
            d = get_distance(h, focal_length)
            a = 0 #math.acos(w / ARUCO_TAG_WIDTH)
            tags.append((xid, xx, xy, d, a))
            # tags.append({'id': xid, 'x': xx, 'y': xy, 'distance': d, 'angle': a})
            # cv2.circle(a_image, (int(corners[x][0][0][0]), int(corners[x][0][0][1])), 2, (1, 0, 0), 2)
            # cv2.circle(a_image, (int(point[0]), int(point[1])), 2, (1, 0, 0), 2)
    return tags


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Do stuff')
    parser.add_argument('-c', '--camera', choices=['webcam', 'raspicam', 'potato'], default='webcam',
                        help='Select camera interface, defaults to webcam')
    parser.add_argument('-y', '--height', type=int, default=480, help="Capture height, defaults to 480px")
    parser.add_argument('-x', '--width', type=int, default=720, help="Capture width, defaults to 720px")
    # parser.add_argument('-g', '--gui', type=bool, default=False)
    parser.add_argument('-i', '--camid', type=int, default=0, help="Webcam id, defaults to 0 for auto")
    parser.add_argument('-r', '--resize', type=float, default=0.5, help="Opencv resize factor")



    args = parser.parse_args()
    print("Capturing with %s at %dx%d" % (args.camera, args.width, args.height))

    if args.camera == "potato":
        print("How am I supposed to use a potato you moron?")
        exit(-1)
    elif args.camera == "raspicam":
        import picamera
        from picamera.array import PiRGBArray

        with picamera.PiCamera(sensor_mode=5, resolution=(args.width, args.height), framerate=24) as camera:
            print("Actual resolution: %s@mode=%d, framerate=%d" % (str(camera.resolution), camera.sensor_mode, camera.framerate))

            time.sleep(0.5)
            rawCapture = PiRGBArray(camera)
            rawCapture.truncate(0)
            #camera.start_preview()
            t = time.time()
            a = False
            n = 1
            tot = 0
            try:
                for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
                    s = time.time()
                    cvimage = frame.array
                    cvimaget = cv2.resize(cvimage, None, fx=args.resize, fy=args.resize)
                    # cvimaget = cv2.cvtColor(cvimaget, cv2.COLOR_BGR2GRAY) # no performance gain
                    aruco_tags = detect_and_cal_tags(cvimaget, RASPICAM_FOCAL_LENGTH)
                    rawCapture.truncate(0)
                    t1 = time.time()
                    tot = tot + (t1 - t)
                    if not a:
                        cv2.imwrite('t.jpg', cvimage)
                        cv2.imwrite('tt.jpg', cvimaget)

                        a = True
                    print("dt=%s, at = %f, pt = %f, %s" % (t1 - t, tot/n, t1 - s, aruco_tags))
                    t = t1
                    n = n+1

                    
            except KeyboardInterrupt:
                pass
            finally:
                #camera.stop_preview()
                pass

    else:
        cap = cv2.VideoCapture(args.camid)
        cap.set(cv2.CAP_PROP_FPS, 60)
        print("Camera FPS: %d" % cap.get(cv2.CAP_PROP_FPS))
        try:
            while True:
                ret, frame = cap.read()
                aruco_tags = detect_and_cal_tags(frame, WEBCAM_FOCAL_LENGTH)
                print(aruco_tags)
        except KeyboardInterrupt:
            pass
        finally:
            cap.release()


