import cv2
import cv2.aruco as aruco
import sys


def make_marker(idn):
    tag = aruco.drawMarker(aruco_dict, idn, 700)
    cv2.imwrite("tag_id%s.png" % idn, tag)
    return tag

if len(sys.argv) < 2:
    print("Usage: %s <id1> (to id2)" % sys.argv[0])
aruco_dict = aruco.Dictionary_get(aruco.DICT_6X6_250)
id1 = int(sys.argv[1])

if len(sys.argv) >= 2:
    id2 = int(sys.argv[2])
    for i in range(id1, id2):
        make_marker(i)
else:
    t = make_marker(id1)
    # display
    cv2.imshow('frame', t)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
