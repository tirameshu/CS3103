#!/usr/bin/env python3

import sys, getopt
import socket
import select
import types
import errno
import time
import logging

HOST = '127.0.0.1'  # The server's hostname or IP address
PORT = 65433    # The port used by the server\

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("QNA-SERVER")

def split_message(byte_message):
    message_arr = byte_message.decode().split(": ")
    return message_arr[0], message_arr[1]

def get_q_num(header):
    header_arr = header.split("/")
    return int(header_arr[2])

def get_number_of_questions(header):
    header_arr = header.split("/")
    return int(header_arr[3])

def create_header(student_id, questionNumber):
    return "{}/A/{}: ".format(student_id, questionNumber)

def run(name, id_num):
    logger.debug("setting up port scan for %r, %r", name, id_num)

    matric__num = id_num
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((HOST, PORT))
    # logger.debug(matric__num)
    client_socket.send(str.encode(matric__num))
    try:
        header, body = split_message(client_socket.recv(1024))
    except ConnectionResetError:
        logger.debug("Connection to teacher is not possible at the moment. Please check with your invigilator about this.")
        return
    # logger.debug(header)
    question_count = get_q_num(header)
    number_of_questions = get_number_of_questions(header)
    logger.info(body)     # print first question
    client_socket.setblocking(False)

    while question_count <= number_of_questions:
        answer = input()
        if answer:
            client_socket.send(str.encode(create_header(matric__num, question_count) + answer))
            question_count += 1
            # header, body = split_message(client_socket.recv(1024))
            # logger.debug(body)
            time.sleep(1)
            if question_count > number_of_questions:
                continue
        try:
            header, body = split_message(client_socket.recv(1024))
            question_count = get_q_num(header)
            logger.info(body)     # print consecutive questions received
        except IOError as e:
            if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
                logger.debug('Reading error: {}'.format(str(e)))
                sys.exit()
            continue
        except Exception as e:
            logger.debug('Found error: {}'.format(str(e)))
            sys.exit()
    logger.debug("Closing connection. Test completed.")
    client_socket.close()

if __name__ == "__main__":
    run("NAME", "ID")