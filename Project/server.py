import select
import socket
import time
import re

HOST = "127.0.0.1"
PORT = 65432

HEADER_SIZE = 8

student_count = 0
clients = {}

# returns msg received
# if no msg received, empty string returned
def receive_message(client_soc):
    try:

        decoded_msg = ""
        while '$' not in decoded_msg:
            received = client_soc.recv(1024)
            
            # If we received no data,
            # it is assumed that client closed the connection.
            # The server will try to reach the client (student) again
            # if student establishes connection again

            if not len(received):
                print("No message received.\n")
                return ""

            decoded_msg += received.decode(encoding='utf-8')

        separator = decoded_msg.index("  ")
        size_of_msg = int(decoded_msg[:separator])

        print('Header size: ' + str(size_of_msg))

        # remove final $ symbol
        endIndex = decoded_msg.index('$')
        port_info = decoded_msg[separator + 2:endIndex]
        # print('Info: ' + port_info)

        return port_info

    except Exception as e:

        # If we are here, client closed connection violently, for example by pressing ctrl+c on his script
        # or just lost his connection
        # socket.close() also invokes socket.shutdown(socket.SHUT_RDWR) what sends information about closing the socket (shutdown read/write)
        # and that's also a cause when we receive an empty message

        print(f'Error receiving message: {str(e)}')
        return ""

# def get_port_info(sock):
#     sock.settimeout(2) # 2s to receive
#     port_info = b""
#     try:
#         port_info = sock.recv()
#
#     except socket.timeout:
#         if not port_info:
#             print("No port info received, requesting for resend in 7s.\n")
#             return []
#
#     decoded_port_info = port_info.decode(encoding='utf-8')
#
#     print("Port info received!\n")
#
#     sock.settimeout(20)
#
#     return decoded_port_info

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
        name_parts = re.split("[.]|->", name) # split by . or ->
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

        # client_soc, addr = server_socket.accept()
        #
        # with client_soc:
        #     print("\nConnected by: ")
        #     print(addr)

        sockets_list = [server_socket]
        while True:
            try:
                read_sockets, write_sockets, err_sockets = select.select(sockets_list, [], sockets_list)

                for readable_socket in read_sockets:
                    if readable_socket == server_socket:
                        # new connection received
                        client_soc, addr = server_socket.accept()

                        # assign student a username
                        global student_count
                        user = str(student_count)
                        if (student_count < 10):
                            # pad with a 0
                            user = '0' + str(student_count)
                        client_soc.sendall(b'ASSIGNED_NAME:' + bytearray(user, encoding='utf-8'))

                        student_count += 1

                        sockets_list.append(client_soc)
                        clients[client_soc] = user
                        print(f"\nNew connection by: Student {user} from {addr}")

                        # request for port info
                        client_soc.sendall(b'GET_PORT')
                        print("Requesting for port info\n")

                    # receiving from existing connections
                    else:

                        port_info = receive_message(readable_socket)

                        if not port_info: # nth received, likely student disconnected
                            print(f"No port info received: Student {clients[readable_socket]} disconnected.\n")

                            # cleanup
                            sockets_list.remove(readable_socket)
                            del clients[readable_socket]

                            continue

                        open_apps = parse_port_info(port_info)

                        if open_apps:
                            byte_array = bytearray(", ".join(open_apps), encoding='utf-8')
                            client_soc.sendall(b'CLOSE_PORTS:' + byte_array)
                            print(f"Student {clients[readable_socket]} has unauthorised ports open\n")

                        time.sleep(10)  # not spam client with instructions

                        # quit option removed to prevent user from stopping the port checker
            
            except KeyboardInterrupt:
                break

    server_socket.close()

run()