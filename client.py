import datetime
import KBHit_py
import protocol
import select
from socket import socket, AF_INET, SOCK_STREAM


SERVER_PORT = 5555
SERVER_IP = '127.0.1.1'

def send_message(current_message, name):
    sending_time = datetime.datetime.now()
    
    command =1
    if current_message.startswith("kick"):
        print(f"{sending_time:%H:%M} Me {current_message}")
        current_message = current_message[5:]
        command = 3
    if current_message.startswith("add"):
        print(f"{sending_time:%H:%M} Me {current_message}")
        current_message = current_message[4:]
        command = 2
    else:
        print(f"{sending_time:%H:%M} Me: {current_message}")

    return protocol.create_client_msg(current_message, name, command)

def main():
    name = 'Me'
    while name == "Me" or name.startswith('@'):
        name = input("Enter your username: ")
    try:
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
                    ok, status, server_message = protocol.get_server_msg(c_socket)
                    if ok:
                        print(f"{server_message}")
                    if status in [400, 401]:
                        exit = True
                        break

                for current_message in messages:
                    if my_socket in ready_wr:
                        if current_message == "":
                            messages.remove(current_message)
                            continue

                        my_socket.send(send_message(current_message, name))

                        if current_message == "quit":
                            exit = True
                            break
                        messages.remove(current_message)

                if exit:
                    break
    except BrokenPipeError:
        print("You have been kicked out from the chat.(or you username is already taken)")
if __name__ == "__main__":
    main()