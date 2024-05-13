import KBHit_py
import select
from socket import socket, AF_INET, SOCK_STREAM

SERVER_PORT = 5555
SERVER_IP = '127.0.1.1'

def main():
    with socket(AF_INET, SOCK_STREAM) as my_socket:
        my_socket.connect((SERVER_IP, SERVER_PORT))
        kb = KBHit_py.KBHit()
        messages = []
        string = []

        #name = input("Please enter what would like to send to the server ")

        while True:
            if kb.kbhit():
                c = kb.getch()
                if ord(c) == 10: # ESC
                    string = ''.join(string)
                    messages.append(string)
                    string= []
                else:
                    string.append(c)

            ready_rd , ready_wr , in_error = select.select([my_socket], [my_socket], [])

            for c_socket in ready_rd:
                message = c_socket.recv(1024).decode()
                print(f"Got from another client: {message}")

            for message in messages:
                if my_socket in ready_wr:
                    print(f"Sending: {message}")
                    my_socket.send(message.encode())
                    messages.remove(message)

if __name__ == "__main__":
    main()