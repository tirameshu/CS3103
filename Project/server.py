import select
import socket
import time
import re

HOST = "127.0.0.1"
PORT = 65432

def get_port_info(sock):
    sock.settimeout(2)
    port_info = b""
    received = sock.recv(1024)
    try:
        while received:
            port_info += received
            received = sock.recv(1024)

    except socket.timeout:
        if not port_info:
            print("No port info received, requesting for resend in 7s.\n")
            return []

    decoded_port_info = port_info.decode(encoding='utf-8')

    print("port info received!\n")

    return decoded_port_info

# return list of ports open for listening and sending
def parse_port_info(lsof_info):
    if not lsof_info:
        return []
    split_port_info = re.split("\n", lsof_info) # split by \n first
    nested_list = list(map(lambda x: re.split("\s+", x), split_port_info)) # split by whitespace in general
    nested_list = list(filter(lambda x: len(x) > 1, nested_list))
    # print(nested_list)

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
            open_apps.append(cmd)


def run():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()

        client_soc, addr = s.accept()

        with client_soc:
            print("Connected by: ")
            print(addr)
            print("\n")

            unauthorised_ports_open = False

            while True:
                time.sleep(7) # check ports every 7s

                if unauthorised_ports_open:
                    client_soc.sendall(b'close ports')
                    print("client has unauthorised ports open\n")
                else:
                    client_soc.sendall(b'ports')
                    print("requesting for port info\n")

                port_info = get_port_info(client_soc)  # recurring, other processes may require separate port
                parse_port_info(port_info)

                # quit option removed to prevent user from stopping the port checker

run()