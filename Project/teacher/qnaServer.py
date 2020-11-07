#!/usr/bin/env python3

import socket
import select
import types
import sys
import logging
import _thread

HOST = '127.0.0.1'  # Standard loopback interface address (localhost)
PORT = 65433        # Port to listen on (non-privileged ports are > 1023)

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("QNA-CLIENT")

sockets_list = [] # change to append in run function
answers = {}

clients = []

questions = [
    "Which animal is a mammal? \n a) Platypus \n b) Duck \n c) Butterfly",
    "Water boils at 317oC \n a) True \n b) False\n",
    "Oil, natural gas and coal are examples of... \n a) Fossil Fuels \n Geothermal resources \n Renewable resources \n Biofuels \n",
    "Which is not a group of organic compounds? \n a) Alkones \n b) Alkynes \n c) Alkenes \n d) Alkanes\n",
    "Which is not made up of crystals? \n a) Feldspar \n b) Sugar \n c) Snow \n d) Glass\n",
    "Which of these planets is second from the Sun and has no moon? \n a) Saturn \n b) Mars \n c) Venus \n d) Jupiter\n"
]
num_questions = len(questions)

def split_message(byte_message):
    message_arr = byte_message.decode().split(": ")
    return message_arr[0], message_arr[1]

def split_answer_header(header):
    header_arr = header.split("/")
    return header_arr[0], header_arr[1], int(header_arr[2])

def receive_message(client_socket):
    try:
        return client_socket.recv(1024)
    except:
        # this means client closed connection violently, or lost connection
        return False

def create_header(student_id, questionNumber):
    return "{}/Q/{}: ".format(student_id, questionNumber)

def create_first_header(student_id, questionNumber, numberOfQuestions):
    return "{}/Q/{}/{}: ".format(student_id, questionNumber, numberOfQuestions)

def print_question(question_number):
    return "{}. {}".format(question_number, questions[question_number - 1])

def run():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen()
    logger.debug("Listening for connections on {}: {}".format(HOST, PORT))

    sockets_list.append(server_socket) # add to socket list

    while True:
        read_sockets, write_sockets, exception_sockets = select.select(sockets_list, [], sockets_list)

        # iterate over notified sockets
        for notified_socket in read_sockets:
            # if notified socket is a server socket, it's a new connection. accept it.
            if notified_socket == server_socket:
                # accept new student
                client_socket, client_address = server_socket.accept()
                sockets_list.append(client_socket)
                clients.append(client_socket)
                logger.debug("Accepted new connection from {}".format(client_address))
                new_student_id = receive_message(client_socket).decode()

                # send welcome message and first question
                logger.debug("New student sign-in as {}".format(new_student_id))
                welcome_message = "Welcome, {}\n".format(new_student_id)
                client_socket.send(str.encode(create_first_header(new_student_id, 1, num_questions) + welcome_message + print_question(1)))
                logger.debug("Question {} sent to {}".format(1, client_address))
            # this means existing socket is sending a message
            else:
                message = receive_message(notified_socket)
                logger.debug("MESSAGE")
                logger.debug(message)
                if message is False:
                    logger.debug("Closed connection from: {}".format(notified_socket))
                    sockets_list.remove(notified_socket)
                    clients.remove(notified_socket)
                    continue
                
                # receive message and add to answers otherwise
                header, body = split_message(message)
                student_id, message_type, question_number = split_answer_header(header)
                if student_id in answers:   # add answers to array
                    answers[student_id].append(body)
                else:   # handle first answers
                    answers[student_id] = [body]
                logger.debug("Answer received: {}".format(body))

                if question_number == num_questions:    # upon receiving answer to last question, close connection
                    logger.debug("Closed connection from {}. Test completed.".format(student_id))
                    logger.debug("Student answers from {}: {}".format(student_id, answers[student_id]))
                    # notified_socket.close()
                    sockets_list.remove(notified_socket)
                    clients.remove(notified_socket)
                    continue

                notified_socket.send(str.encode(create_header(student_id, question_number + 1) + print_question(question_number + 1)))

    # execute after exit from while loop
    for notified_socket in exception_sockets:
        sockets_list.remove(notified_socket)
        clients.remove(notified_socket)

if __name__ == "__main__":
    run()

