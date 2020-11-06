#!/usr/bin/env python3

import socket
import select
import types
import sys
import _thread

HOST = '127.0.0.1'  # Standard loopback interface address (localhost)
PORT = 65432        # Port to listen on (non-privileged ports are > 1023)

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((HOST, PORT))
server_socket.listen()
print("Listening for connections on {}: {}".format(HOST, PORT))

sockets_list = [server_socket]
answers = {}

clients = []

questions = [
    "Which animal is a mammal? \n a) Platypus \n b) Duck \n c) Butterfly",
    "Water boils at 317oC \n a) True \n b) False\n"
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
            print("Accepted new connection from {}".format(client_address))
            new_student_id = receive_message(client_socket).decode()

            # send welcome message and first question
            print("New student sign-in as {}".format(new_student_id))
            welcome_message = "Welcome, {}\n".format(new_student_id)
            client_socket.send(str.encode(create_first_header(new_student_id, 1, num_questions) + welcome_message + print_question(1)))
            print("Question {} sent to {}".format(1, client_address))
        # this means existing socket is sending a message
        else:
            message = receive_message(notified_socket)
            print("MESSAGE")
            print(message)
            if message is False:
                print("Closed connection from: {}".format(notified_socket))
                sockets_list.remove(notified_socket)
                clients.remove(notified_socket)
                continue
            
            # receive message and add to answers otherwise
            header, body = split_message(message)
            student_id, message_type, question_number = split_answer_header(header)
            if student_id in answers:
                answers[student_id].append(body)
            else:   # handle first answers
                answers[student_id] = [body]
            print("Answer received: {}".format(body))

            if question_number == num_questions:
                print("Closed connection from {}. Test completed.".format(student_id))
                print(answers[student_id])
                notified_socket.close()
                sockets_list.remove(notified_socket)
                clients.remove(notified_socket)
                continue

            notified_socket.send(str.encode(create_header(student_id, question_number + 1) + print_question(question_number + 1)))
            # broadcast to all connected clients
            # modified_message = 
            # for client_socket in clients:
            #     print("Sending message FROM: {} TO: {} - {}".format(notified_socket, client_socket, message))
            #     client_socket.send(message)
for notified_socket in exception_sockets:
    sockets_list.remove(notified_socket)
    clients.remove(notified_socket)