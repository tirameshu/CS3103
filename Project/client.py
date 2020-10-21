# scans local ports
import socket

MAX_PORT = 65535

def scan_ports():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(0.1)

    # port = 80

    # code = s.connect_ex(("localhost", port))
    # s.close()

    # if not code:
    #     print("[+] port " + str(port))
    # else:
    #     print("[-] port " + str(port))

    for port in range(1, MAX_PORT + 1):
        code = s.connect_ex(("0.0.0.0", port))

        if code == 0 : # successful
            print("[+] port " + str(port))
        # else:
        #     print("[-] port " + str(port))

    s.close()

scan_ports()