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
answers = []

clients = []

def receive_message(client_socket):
    try:
        return client_socket.recv(1024)
    except:
        # this means client closed connection violently, or lost connection
        return False

while True:
    read_sockets, write_sockets, exception_sockets = select.select(sockets_list, [], sockets_list)

    # iterate over notified sockets
    for notified_socket in read_sockets:
        # if notified socket is a server socket, it's a new connection. accept it.
        if notified_socket == server_socket:
            client_socket, client_address = server_socket.accept()
            sockets_list.append(client_socket)
            clients.append(client_socket)
            print("Accepted new connection from {}".format(client_address))
            client_socket.send(str.encode("QUESTION: Which animal is a mammal? \n a) Platypus \n b) Duck \n c) Butterfly\n"))
            print("Question sent to {}".format(client_address))
        # this means existing socket is sending a message
        else:
            message = receive_message(notified_socket)
            if message is False:
                print("Closed connection from: {}".format(notified_socket))
                sockets_list.remove(notified_socket)
                clients.remove(notified_socket)
                continue
            
            # receive message and add to answers otherwise
            answers.append(message)
            print("Answer received: {}".format(message.decode()))

            # broadcast to all connected clients
            # modified_message = 
            # for client_socket in clients:
            #     print("Sending message FROM: {} TO: {} - {}".format(notified_socket, client_socket, message))
            #     client_socket.send(message)
for notified_socket in exception_sockets:
    sockets_list.remove(notified_socket)
    clients.remove(notified_socket)


# sel = selectors.DefaultSelector()

# def accept_wrapper(sock):
#     conn, addr = sock.accept()  # Should be ready to read
#     print("accepted connection from", addr)
#     conn.setblocking(False)
#     data = types.SimpleNamespace(addr=addr, inb=b"", outb=b"")
#     events = selectors.EVENT_READ | selectors.EVENT_WRITE
#     sel.register(conn, events, data=data)


# def service_connection(key, mask):
#     sock = key.fileobj
#     data = key.data
#     if mask & selectors.EVENT_READ:
#         recv_data = sock.recv(1024)  # Should be ready to read
#         if recv_data:
#             data.outb += recv_data
#         else:
#             print("closing connection to", data.addr)
#             sel.unregister(sock)
#             sock.close()
#     if mask & selectors.EVENT_WRITE:
#         if data.outb:
#             print("echoing", repr(data.outb), "to", data.addr)
#             sent = sock.send(data.outb)  # Should be ready to write
#             data.outb = data.outb[sent:]


# if len(sys.argv) != 3:
#     print("usage:", sys.argv[0], "<host> <port>")
#     sys.exit(1)

# host, port = sys.argv[1], int(sys.argv[2])
# server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
# server.bind((HOST, PORT))
# server.listen(100)
# print("listening on", (HOST, PORT))

# list_of_clients = []

# def clientthread(conn, addr): 
#     conn.send(str.encode("Welcome to this chatroom!"))
#     while True:
#         try:
#             message = str.decode(conn.recv(1024))
#             if message:
#                 message_to_send = "<{}> {}".format(addr[0], message)
#                 print(message_to_send)
#                 broadcast(message_to_send, conn)
#             else:
#                 remove(conn)
#         except:
#             continue
# def broadcast(message, connection):
#     print("CLIENTS TO SEND TO: ")
#     print(list_of_clients)
#     for client in list_of_clients:
#         # if client != connection:
#             try:
#                 client.send(message)
#             except:
#                 client.close()
#                 remove(client)
#     print(list_of_clients)

# def remove(connection):
#     if connection in list_of_clients:
#         list_of_clients.remove(connection)

# while True:
#     conn, addr = server.accept()
#     list_of_clients.append(conn)
#     print(addr[0] + " connected")
#     print(list_of_clients)
#     _thread.start_new_thread(clientthread, (conn, addr))

# conn.close()
# server.close()

# lsock.setblocking(False)
# sel.register(lsock, selectors.EVENT_READ, data=None)

# try:
#     while True:
#         events = sel.select(timeout=None)
#         for key, mask in events:
#             if key.data is None:
#                 accept_wrapper(key.fileobj)
#             else:
#                 service_connection(key, mask)
# except KeyboardInterrupt:
#     print("caught keyboard interrupt, exiting")
# finally:
#     sel.close()
