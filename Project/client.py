# scans local ports
import socket
import subprocess

MAX_PORT = 65535

HOST = "127.0.0.1"
PORT = 65432 # has to be hardcoded

def get_apps(sock):
    sock.settimeout(2)  # 2s to receive
    app_info = b""
    received = sock.recv(1024)
    try:
        while received:
            app_info += received
            received = sock.recv(1024)

    except socket.timeout:
        if not app_info:
            print("No app info received, server will resend in 5s.\n")
            return []

    decoded_app_info = app_info.decode(encoding='utf-8')

    sock.settimeout(20)

    return decoded_app_info

def list_ports():
    cmd = "sudo lsof -i -P -n | grep -e LISTEN -e ESTABLISHED"

    output = subprocess.check_output(cmd, shell=True)

    output = output.decode(encoding='utf-8')
    return output

def process_ports(output):
    print(output)

def run():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        if s.connect_ex((HOST, PORT)) == 0:

            print("Connected with host!\n")
            while True:
                # wait for instruction
                instruction = s.recv(1024).decode(encoding='utf-8')
                if instruction == "GET_PORT":
                    port_info = list_ports()
                    print("Fetching port info...\n")
                    s.sendall(port_info.encode(encoding='utf-8'))
                    print("Port info sent!\n")
                elif "CLOSE_PORTS" in instruction:
                    print("Close these apps: ")

                    index = instruction.index(":")
                    apps = instruction[index+1:]
                    print(apps)

run()