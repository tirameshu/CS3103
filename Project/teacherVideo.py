import socket
import multiprocessing
import cv2
import numpy as np
import pyautogui
import os
import sys

HOST = '127.0.0.1' 
PORT = 65432        

os.environ['DISPLAY'] = ':0'

# display screen resolution, get it from your OS settings
SCREEN_SIZE = (1920, 1080)

# define the codec
fourcc = cv2.VideoWriter_fourcc(*"XVID")

# create the video write object
# out = cv2.VideoWriter("teacher.avi", fourcc, 5.0, (SCREEN_SIZE))

def studentVideoHandler(connection, address):

    import logging
    import random
    import cv2
    import numpy as np

    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger("process-%r" % (address,))
    vid_out = cv2.VideoWriter("client" + str(address[1]) + ".avi", fourcc, 5.0, (SCREEN_SIZE))
    frame_size = -1
    counter = 0
    try:
        logger.debug("Connected %r at %r", connection, address)
        while True:
            logger.debug("Waiting for next frame")
            inp = connection.recv(65482)
            data = b''
            while inp:
                data = data + inp
                if sys.getsizeof(inp) < 65482:
                    break
                inp = connection.recv(65482)
            frame = np.frombuffer(data, dtype="uint8")
            if frame_size < 0:
                frame_size = frame.size
            if frame.size != frame_size:
                continue
            logger.debug("Received frame size %r", frame.size)
            frame = np.reshape(frame, (1080, 1920, -1))

            # convert colors from BGR to RGB
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # write the frame
            vid_out.write(frame)

            # show the frame
            # cv2.imshow("screenshot", frame)

            connection.send('ACK{counter}'.format(counter = counter).encode())
            counter = counter + 1
            # print(frame.shape)

    except:
        logger.exception("Problem handling request")
    finally:
        logger.debug("Closing socket")
        connection.close()

class Server(object):
    def __init__(self, hostname, port):
        import logging
        self.logger = logging.getLogger("teacher server")
        self.hostname = hostname
        self.port = port

    def start(self):
        self.logger.debug("listening")
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((self.hostname, self.port))
        self.socket.listen(1)

        while True:
            conn, address = self.socket.accept()
            self.logger.debug("Got connection")
            process = multiprocessing.Process(target=studentVideoHandler, args=(conn, address))
            process.daemon = True
            process.start()
            self.logger.debug("Started process %r", process)


if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.DEBUG)
    server = Server(HOST, PORT)
    try:
        logging.info("Listening")
        server.start()
    except:
        logging.exception("Unexpected exception")
    finally:
        logging.info("Shutting down")
        for process in multiprocessing.active_children():
            logging.info("Shutting down process %r", process)
            process.terminate()
            process.join()
    cv2.destroyAllWindows()
    out.release()
    logging.info("All done")

# make sure everything is closed when exited