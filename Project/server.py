import select
import socket
import time
import re

HOST = "127.0.0.1"
PORT = 65432

HEADER_SIZE = 8
FIXED_LENGTH = 1024

# returns msg received
# if no msg received, empty string returned
def receive_message(client_soc):
    try:

        # Receive size of msg first
        received = client_soc.recv(HEADER_SIZE)
        print(received.decode(encoding='utf-8'))

        # If we received no data, client gracefully closed a connection, for example using socket.close() or socket.shutdown(socket.SHUT_RDWR)
        if not len(received):
            print("nothing received\n")
            return ""

        size_of_msg = int(received.decode(encoding='utf-8').strip())

        print('header:' + str(size_of_msg))

        return client_soc.recv(size_of_msg).decode(encoding='utf-8')

    except Exception as e:

        # If we are here, client closed connection violently, for example by pressing ctrl+c on his script
        # or just lost his connection
        # socket.close() also invokes socket.shutdown(socket.SHUT_RDWR) what sends information about closing the socket (shutdown read/write)
        # and that's also a cause when we receive an empty message

        print(str(e))
        return ""

def get_port_info(sock):
    sock.settimeout(2) # 2s to receive
    port_info = b""
    try:
        port_info = sock.recv()

    except socket.timeout:
        if not port_info:
            print("No port info received, requesting for resend in 7s.\n")
            return []

    decoded_port_info = port_info.decode(encoding='utf-8')

    print("Port info received!\n")

    sock.settimeout(20)

    return decoded_port_info

# return list of ports open for listening and sending
def parse_port_info(lsof_info):
    if not lsof_info:
        return []

    split_port_info = re.split("\n", lsof_info) # split by \n first
    nested_list = list(map(lambda x: re.split("\s+", x), split_port_info)) # split by whitespace in general
    nested_list = list(filter(lambda x: len(x) > 1, nested_list)) # filter out [""]

    """
    1) filter those involving MAC addresses, localhost, 127.0.0.1
    - assumed to be necessary local bgkd processes
    - even if some (unauthorised) applications still have processes involving localhost,
    they have other processes involving external ip that will be captured
    2) keep track of a list of applications that are open, and don't need to check all entries
    for the same application
    3) return to client the list of apps to close
    """

    external_processes = list(filter(lambda x: "localhost" not in x[8] and "127.0.0.1" not in x[8] and "::" not in x[8], nested_list))

    open_apps = []

    for entry in external_processes:
        cmd, pid, user, fd, ftype, device, size_off, node, name, status = entry
        name_parts =re.split("[.]|->", name) # split by . or ->
        port = 0
        for part in name_parts:
            if ":" in part:
                port = int(part[part.index(":")+1:]) # take port number
                break

        if port != PORT:
            if cmd not in open_apps:
                open_apps.append(cmd)

    print(open_apps)
    return open_apps


def run():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((HOST, PORT))
        server_socket.listen()

        client_soc, addr = server_socket.accept()

        with client_soc:
            print("\nConnected by: ")
            print(addr)

            # sockets_list = [server_socket]
            while True:
                # read_sockets, write_sockets, err_sockets = select.select(sockets_list, [], sockets_list)
                #
                # for readable_socket in read_sockets:
                #     if readable_socket == server_socket:
                #         # new connection received
                #         client_soc, addr = server_socket.accept()
                #         user = receive_message(server_socket)


                client_soc.sendall(b'GET_PORT')
                print("Requesting for port info\n")

                port_info = receive_message(client_soc)
                open_apps = parse_port_info(port_info)

                if open_apps:
                    byte_array = bytearray(", ".join(open_apps), encoding='utf-8')
                    client_soc.sendall(b'CLOSE_PORTS:' + byte_array)
                    print("Client has unauthorised ports open\n")

                time.sleep(10) # not spam client with instructions

                # quit option removed to prevent user from stopping the port checker

run()