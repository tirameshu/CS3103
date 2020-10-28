# scans local ports
import socket
import subprocess

MAX_PORT = 65535

HOST = "127.0.0.1"
PORT = 65432 # has to be hardcoded

def list_ports():
    cmd = "sudo lsof -i -P -n | grep -e LISTEN -e ESTABLISHED"

    output = subprocess.check_output(cmd, shell=True)

    output = output.decode(encoding='utf-8')
    return output

def process_ports(output):
    print(output)

def run():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(10)
        if s.connect_ex((HOST, PORT)) == 0:

            print("Connected with host!\n")
            while True:
                port_info = list_ports()
                print("Port info...\n")
                process_ports(port_info[:100])  # for verification

                # wait for instruction
                instruction = s.recv(1024).decode(encoding='utf-8')
                if instruction == "ports":
                    s.sendall(port_info.encode(encoding='utf-8'))
                    print("port info sent!\n")
                else:
                    print("no instruction!\n")

run()