import socket
import time
import re

HOST = "127.0.0.1"
PORT = 65432

def get_port_info(conn):
    port_info = b""
    received = conn.recv(1024)
    while received:
        print("receiving")
        port_info += received
        received = conn.recv(1024)

        time.sleep(1)
        if port_info + received == port_info:
            break


    print("out of loop\n")
    decoded_port_info = port_info.decode(encoding='utf-8')

    print("port info received...\n")
    print(decoded_port_info[:100]) # print a bit just to see

    return decoded_port_info

def parse_port_info(port_info):
    print("splitting\n")
    splitted_port_info = list(filter(lambda x: x, re.split("\s", port_info)))
    print(splitted_port_info[:20])

def run():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(2)
        s.bind((HOST, PORT))
        s.listen()

        conn, addr = s.accept()

        with conn:
            print("Connected by: ")
            print(addr)
            print("\n")

            while True:
                time.sleep(5) # sleep 5s before checking again
                conn.sendall(b'ports')
                print("requesting for port info\n")

                port_info = get_port_info(conn)  # recurring, other processes may require separate port
                parse_port_info(port_info)

                # quit option removed to prevent user from stopping the port checker

run()