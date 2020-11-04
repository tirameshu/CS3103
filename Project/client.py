# scans local ports
import socket
import subprocess
import time
import logging

HOST = "127.0.0.1"
PORT = 65432 # has to be hardcoded
USERNAME = "Unassigned"

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("PORTSCAN-CLIENT")

def send_message(sock, msg):
    # send size of msg together with port info
    # message format is size and body separated by 2 spaces and ending with a $
    # [size]  [body content]$

    full_msg = (str(len(msg)) + "  " + msg + "$").encode(encoding='utf-8')
    sock.sendall(full_msg)

    logger.debug("Message sent!\n")

def list_ports():
    cmd = "sudo lsof -i -P -n | grep -e LISTEN -e ESTABLISHED"

    output = subprocess.check_output(cmd, shell=True)

    output = output.decode(encoding='utf-8')
    return output

def run(name, id_num):
    logger.debug("setting up port scan for %r, %r", name, id_num)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        if s.connect_ex((HOST, PORT)) == 0:
            logger.debug("Connected with host!\n")

            # receive assigned name
            # currently only reads 2-bytes names
            instruction = s.recv(16).decode(encoding='utf-8')
            index = instruction.index(":")
            USERNAME = str(instruction[index + 1:])
            logger.debug("Assigned name: Student " + USERNAME)

            while True:
                # wait for instruction
                instruction = s.recv(1024).decode(encoding='utf-8')
                if instruction == "GET_PORT":
                    # run command
                    port_info = list_ports()
                    logger.debug("Fetching port info...\n")

                    send_message(s, port_info)
                elif "CLOSE_PORTS" in instruction:
                    logger.debug("Close these apps: ")
                    # instruction in format
                    # CLOSE_PORTS: app1, app2, ...
                    index = instruction.index(":")
                    apps = instruction[index+1:]
                    logger.debug(apps)

if __name__ == "__main__":
    run()