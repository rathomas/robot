'''
Created on Oct 14, 2013

@author: rthomas
'''
import cv2

# setup video capture
cap = cv2.VideoCapture(0)

while True:
    ret,im = cap.read()
    cv2.imshow('video test',im)
    key = cv2.waitKey(10)
    if key == 27:
        break
    if key == ord(' '):
        cv2.imwrite('vid_result.jpg',im)