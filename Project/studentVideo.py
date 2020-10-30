import cv2
import numpy as np
import pyautogui
import os
import socket
import time
import sys
import select

HOST = '127.0.0.1'  
PORT = 65432    

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))

while True:
    # make a screenshot
    img = pyautogui.screenshot()

    # convert these pixels to a proper numpy array to work with OpenCV
    frame = np.array(img)

    frame.flatten()

    byte = frame.tobytes()

    s.send(byte)

    s.settimeout(1)
    try:
    	data = s.recv(1024)
    	print(data.decode())

    except:
    	print('timeout')

# os.environ['DISPLAY'] = ':0'

# # display screen resolution, get it from your OS settings
# SCREEN_SIZE = (1920, 1080)

# # define the codec
# fourcc = cv2.VideoWriter_fourcc(*"XVID")

# # create the video write object
# out = cv2.VideoWriter("output.mp4", fourcc, 5.0, (SCREEN_SIZE))

# while True:

#     # make a screenshot
#     img = pyautogui.screenshot()

#     # convert these pixels to a proper numpy array to work with OpenCV
#     frame = np.array(img)

#     # print(frame)
#     frame = frame.flatten()

#     byte = frame.tobytes()

#     fframe = np.frombuffer(byte, dtype="uint8")

#     print(frame.shape)
#     print(fframe.shape)

#     fframe = np.reshape(fframe, (1080, 1920, 3))

#     # convert colors from BGR to RGB
#     fframe = cv2.cvtColor(fframe, cv2.COLOR_BGR2RGB)

#     # write the frame
#     out.write(fframe)


#     # show the frame
#     # cv2.imshow("screenshot", frame)

#     # if the user clicks q, it exits
#     if cv2.waitKey(1) == ord("q"):
#         break

# # make sure everything is closed when exited
# cv2.destroyAllWindows()
# out.release()
