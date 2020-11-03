import numpy as np
import pyautogui
import os
import socket
import time
import sys
import select
import threading as th
import keyboard

keep_going = True

def key_capture_thread():
    global keep_going
    input()
    keep_going = False

HOST = '127.0.0.1'
PORT = 65432

name = input('Name: ')
id_num = input('ID: ')

hello = 'hello:{name}:{id}'.format(name=name, id=id_num)

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))

s.send(hello.encode())
ack = s.recv(1024)

if ack.decode() != 'ACK':
    print('Error')
    exit(1)

input('Press enter to start recording')

cont = True

th.Thread(target=key_capture_thread, args=(), name='key_capture_thread', daemon=True).start()

while cont:

    while keep_going:
        # make a screenshot
        img = pyautogui.screenshot()

        # convert these pixels to a proper numpy array to work with OpenCV
        frame = np.array(img)

        frame.flatten()

        byte = frame.tobytes()

        s.send(b'video' + byte)

        s.settimeout(1)

        try:
            data = s.recv(1024)
            print(data.decode())

            if data == b'done':
                print('Recording stopped by teacher')
                cont = False
                keep_going = False

        except Exception as e:
            print('timeout')

    if cont == False:
        break
        
    print('You paused the recording')

    s.send('pause'.encode())

    while ack.decode() != 'PSE_ACK':
        ack = s.recv(1024)

    resume = input('Recording paused. Resume? ')

    if resume == 'yes':
        s.send(b'resume')
        while ack.decode() != 'RES_ACK':
            ack = s.recv(1024)
        keep_going = True
        th.Thread(target=key_capture_thread, args=(), name='key_capture_thread', daemon=True).start()

    else:
        s.send(b'stop')
        while ack.decode() != 'STP_ACK':
            ack = s.recv(1024)
        cont = False

