#!/usr/bin/env python3

import sys, getopt
import socket
import select
import types
import errno
import time

HOST = '127.0.0.1'  # The server's hostname or IP address
PORT = 65432    # The port used by the server

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

matric__num = input('MATRIC NUMBER: ')
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((HOST, PORT))
print(matric__num)
client_socket.send(str.encode(matric__num))
header, body = split_message(client_socket.recv(1024))
print(header)
question_count = get_q_num(header)
number_of_questions = get_number_of_questions(header)
print(body)     # print first question
client_socket.setblocking(False)

while question_count <= number_of_questions:
    answer = input()
    if answer:
        client_socket.send(str.encode(create_header(matric__num, question_count) + answer))
        question_count += 1
        # header, body = split_message(client_socket.recv(1024))
        # print(body)
        time.sleep(1)
        if question_count > number_of_questions:
            continue
    try:
        header, body = split_message(client_socket.recv(1024))
        question_count = get_q_num(header)
        print(body)     # print first question
    except IOError as e:
        if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
            print('Reading error: {}'.format(str(e)))
            sys.exit()
        continue
    except Exception as e:
        print('Found error: {}'.format(str(e)))
        sys.exit()
print("Closing connection. Test completed.")
client_socket.close()

    # maintains list of possible input streams
    # sockets_list = [sys.stdin, server]

    # read_sockets, write_socket, error_socket = select.select(sockets_list, [], [])

    # for socks in read_sockets:
    #     if socks == server:
    #         message = socks.recv(2048)
    #         print(message)
    #     else:
    #         message = sys.stdin.readline
    #         server.send(message)
    #         sys.stdout.write("<You> {}".format(message))
    #         sys.stdout.flush()
# server.close()

# sel = selectors.DefaultSelector()
# messages = [b"Message 1 from client.", b"Message 2 from client."]

# def start_connections(host, port, num_conns):
#     server_addr = (host, port)
#     for i in range(0, num_conns):
#         connid = i + 1
#         print("starting connection", connid, "to", server_addr)
#         sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#         sock.setblocking(False)
#         sock.connect_ex(server_addr)
#         events = selectors.EVENT_READ | selectors.EVENT_WRITE
#         data = types.SimpleNamespace(
#             connid=connid,
#             msg_total=sum(len(m) for m in messages),
#             recv_total=0,
#             messages=list(messages),
#             outb=b"",
#         )
#         sel.register(sock, events, data=data)


# def service_connection(key, mask):
#     sock = key.fileobj
#     data = key.data
#     if mask & selectors.EVENT_READ:
#         recv_data = sock.recv(1024)  # Should be ready to read
#         if recv_data:
#             print("received", repr(recv_data), "from connection", data.connid)
#             data.recv_total += len(recv_data)
#         if not recv_data or data.recv_total == data.msg_total:
#             print("closing connection", data.connid)
#             sel.unregister(sock)
#             sock.close()
#     if mask & selectors.EVENT_WRITE:
#         if not data.outb and data.messages:
#             data.outb = data.messages.pop(0)
#         if data.outb:
#             print("sending", repr(data.outb), "to connection", data.connid)
#             sent = sock.send(data.outb)  # Should be ready to write
#             data.outb = data.outb[sent:]


# if len(sys.argv) != 2:
#     print("usage:", sys.argv[0], "<num_connections>")
#     sys.exit(1)

# num_conns = sys.argv[1]
# start_connections(HOST, PORT, int(num_conns))

# try:
#     while True:
#         events = sel.select(timeout=1)
#         if events:
#             for key, mask in events:
#                 service_connection(key, mask)
#         # Check for a socket being monitored to continue.
#         if not sel.get_map():
#             break
# except KeyboardInterrupt:
#     print("caught keyboard interrupt, exiting")
# finally:
#     sel.close()