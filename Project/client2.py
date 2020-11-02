# scans local ports
import socket
import subprocess
import time

HOST = "127.0.0.1"
PORT = 65432 # has to be hardcoded

def send_message(sock, msg):
    # send size of msg then port info
    sock.sendall(str(len(msg)).encode(encoding='utf-8'))
    print("sending msg of size " + str(len(msg)))

    time.sleep(1)

    sock.sendall(msg.encode(encoding='utf-8'))
    print("Message sent!\n")

def list_ports():
    cmd = "sudo lsof -i -P -n | grep -e LISTEN -e ESTABLISHED"

    output = subprocess.check_output(cmd, shell=True)

    output = output.decode(encoding='utf-8')
    return output

def run():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        if s.connect_ex((HOST, PORT)) == 0:

            print("Connected with host!\n")

            send_message(s, "B") # username

            while True:
                # wait for instruction
                instruction = s.recv(1024).decode(encoding='utf-8')
                if instruction == "GET_PORT":
                    # run command
                    port_info = list_ports()
                    print("Fetching port info...\n")

                    send_message(s, port_info)

                elif "CLOSE_PORTS" in instruction:
                    print("Close these apps: ")
                    # instruction in format
                    # CLOSE_PORTS: app1, app2, ...
                    index = instruction.index(":")
                    apps = instruction[index+1:]
                    print(apps)

run()