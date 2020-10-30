#!/usr/bin/env python3

import sys
import socket
import select
import types
import errno

HOST = '127.0.0.1'  # The server's hostname or IP address
PORT = 65432      # The port used by the server

username = input('USERNAME FOR CHAT: ')
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((HOST, PORT))
welcome_message = client_socket.recv(1024)
print(welcome_message.decode())
client_socket.setblocking(False)

while True:
    message = input()
    if message:
        # print("<You>: {}".format(message))
        client_socket.send(str.encode(message))
    try:
        while True:
            recpt = client_socket.recv(1024)
            # if not len(recpt):
            #     print('Connection closed by server')
            #     sys.exit()
            print(recpt)
    except IOError as e:
        if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
            print('Reading error: {}'.format(str(e)))
            sys.exit()
        continue
    except Exception as e:
        print('Found error: {}'.format(str(e)))
        sys.exit()


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