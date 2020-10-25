import socket

HOST = "127.0.0.1"
PORT = 65432

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()

    conn, addr = s.accept()

    with conn:
        print(addr)
        print("Connected by: ")
        print(addr)
        print("\n")

        flag = False
        while not flag:
            conn.sendall(b'ports')
            flag = True
            data = b""
            received = conn.recv(1024)
            while received:
                data += received
                received = conn.recv(1024)

            decoded = data.decode(encoding='utf-8')

            print("data received...\n")
            print(data.decode(encoding='utf-8'))

            if decoded == "quit":
                break