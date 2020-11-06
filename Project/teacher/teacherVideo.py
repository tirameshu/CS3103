import socket
import multiprocessing
import cv2
import numpy as np
import os
import sys

HOST = '127.0.0.1'
PORT = 65442    

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
    logger = logging.getLogger("VIDEOSTREAM-process-%r" % (address,))
    frame_size = -1
    counter = 0
    try:
        logger.debug("Connected %r at %r", connection, address)

        stu_data = connection.recv(1024)
        stu_data = stu_data.decode()

        stu_info = stu_data.split(':')

        logger.debug('Established connection with {name}({number})'.format(name=stu_info[1], number=stu_info[2]))
        connection.send(b'ACK')

        vid_out = cv2.VideoWriter('video/' + str(stu_info[1]) + '(' + str(stu_info[2]) + ").avi", fourcc, 5.0, (SCREEN_SIZE))

        record = True

        while record:
            # logger.debug("Waiting for next frame")
            inp = connection.recv(65482)
            if inp == 'pause'.encode():
                logger.debug('{number} paused the recording'.format(number=stu_info[2]))
                connection.send(b'PSE_ACK')
                resume = connection.recv(1024)
                if resume.decode() == 'stop':
                    logger.debug('{number} stopped the recording'.format(number=stu_info[2]))
                    record = False
                    connection.send(b'STP_ACK')
                else:
                    logger.debug('{number} resumed the recording'.format(number=stu_info[2]))
                    connection.send(b'RES_ACK')

            elif inp[:5] == 'video'.encode():
                inp = inp[5:]
                data = b''
                while inp:
                    data = data + inp
                    if sys.getsizeof(inp) < 65482:
                        break
                    inp = connection.recv(65482)
                frame = np.frombuffer(data, dtype="uint8")
                if frame.shape[0] < 1080*1920:
                    logger.debug("Frame shape mismatch")
                    continue
                if frame_size < 0:
                    frame_size = frame.size
                    logger.debug("Setting initial frame_size")
                if frame.size != frame_size:
                    logger.debug("Mismatch frame_size received: %r, expected: %r", frame.size, frame_size)
                    continue
                logger.debug("Received frame size %r", frame.shape[0])
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
        connection.send(b'done')
        logger.debug("Closing socket")
        connection.close()

class Server(object):
    def __init__(self, hostname, port):
        import logging
        self.logger = logging.getLogger("VIDEOSTREAM-SERVER")
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

def run():
    import logging
    logging.basicConfig(level=logging.DEBUG)
    server = Server(HOST, PORT)
    try:
        logging.info("Listening")
        server.start()
    except:
        logging.exception("Unexpected exception")
    finally:
        logging.info("Shutting down stream")
        for process in multiprocessing.active_children():
            logging.info("Shutting down process %r", process)
            process.terminate()
            process.join()
    cv2.destroyAllWindows()
    logging.info("Stream shut down done")

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
    logging.info("All done")

# make sure everything is closed when exited
