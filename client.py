import datetime
import KBHit_py
import protocol
import select
from socket import socket, AF_INET, SOCK_STREAM


SERVER_PORT = 5555
SERVER_IP = '127.0.1.1'

def main():
    name = 'Me'
    while name == "Me":
        name = input("Enter your username: ")
    
    with socket(AF_INET, SOCK_STREAM) as my_socket:
        my_socket.connect((SERVER_IP, SERVER_PORT))
        kb = KBHit_py.KBHit()
        messages = []
        string = []

        #name = input("Please enter what would like to send to the server ")

        while True:
            exit = False
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
                ststus, server_message = protocol.get_server_msg(c_socket)
                if ststus:
                    print(f"{server_message}")

            for current_message in messages:
                if my_socket in ready_wr:
                    if current_message == "":
                        messages.remove(current_message)
                        continue
                    
                    sending_time = datetime.datetime.now()
                    print(f"{sending_time:%H:%M} Me: {current_message}")
                    my_socket.send(protocol.create_client_msg(current_message, name))
                    
                    if current_message == "quit":
                        exit = True
                        break
                    messages.remove(current_message)
            
            if exit:
                break

if __name__ == "__main__":
    main()