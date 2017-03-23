import numpy as np
import cv2
import cv2.aruco as aruco

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FPS, 60)

print("Camera FPS: %d" % cap.get(cv2.CAP_PROP_FPS))

def findmiddle(tag_corners):
    maxx, maxy = max(tag_corners[0][0], tag_corners[1][0], tag_corners[2][0], tag_corners[3][0]), \
                 max(tag_corners[0][1], tag_corners[1][1], tag_corners[2][1], tag_corners[3][1])

    minx, miny = min(tag_corners[0][0], tag_corners[1][0], tag_corners[2][0], tag_corners[3][0]), \
                 min(tag_corners[0][1], tag_corners[1][1], tag_corners[2][1], tag_corners[3][1])
    return (maxx + minx) / 2, (maxy + miny) / 2, maxx - minx, maxy - miny


while True:
    # Capture frame-by-frame
    ret, frame = cap.read()
    # print(frame.shape) #480x640
    # Our operations on the frame come here
    gray = frame  # cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    aruco_dict = aruco.Dictionary_get(aruco.DICT_6X6_250)
    parameters = aruco.DetectorParameters_create()

    # print(parameters)

    '''    detectMarkers(...)
        detectMarkers(image, dictionary[, corners[, ids[, parameters[, rejectedI
        mgPoints]]]]) -> corners, ids, rejectedImgPoints
        '''
    # lists of ids and the corners beloning to each id
    corners, ids, rejectedImgPoints = aruco.detectMarkers(gray, aruco_dict, parameters=parameters)
    # print(corners)

    # It's working.
    # my problem was that the cellphone put black all around it. The alrogithm
    # depends very much upon finding rectangular black blobs

    gray = aruco.drawDetectedMarkers(gray, corners, ids)
    print(len(corners))
    for x in range(0, len(corners)):
        point = findmiddle(corners[x][0])
        cv2.circle(gray, (int(corners[x][0][0][0]), int(corners[x][0][0][1])), 2, (1, 0, 0), 2)
        cv2.circle(gray, (int(point[0]), int(point[1])), 2, (1, 0, 0), 2)

    # print(rejectedImgPoints)
    # Display the resulting frame
    cv2.imshow('frame', gray)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()
