import socket
import os
from threading import Thread
import sys
import os.path


SEPARATOR = "<SEPARATOR>"

clients = []
files = {}
lastfilename = ""

# Thread to listen one particular client
class ClientListener(Thread):
    def __init__(self, name: str, sock: socket.socket):
        super().__init__(daemon=True)
        self.sock = sock
        self.name = name

    # add 'me> ' to sended message
    def _clear_echo(self, data):
        # \033[F – symbol to move the cursor at the beginning of current line (Ctrl+A)
        # \033[K – symbol to clear everything till the end of current line (Ctrl+K)
        self.sock.sendall('\033[F\033[K'.encode())
        data = 'me> '.encode() + data
        # send the message back to user
        self.sock.sendall(data)

    # broadcast the message with name prefix eg: 'u1> '
    def _broadcast(self, data):
        data = (self.name + '> ').encode() + data
        for u in clients:
            # send to everyone except current client
            if u == self.sock:
                continue
            u.sendall(data)

    # clean up
    def _close(self):
        #print("HERE")
        clients.remove(self.sock)
        self.sock.close()
        print(self.name + ' disconnected')


    def ReadData(self):
        size = int.from_bytes(self.sock.recv(4), "big")
        return self.sock.recv(size).decode()

    def SendData(self, data_string):
        self.sock.send(len(data_string).to_bytes(4, byteorder='big'))
        self.sock.send(data_string.encode())

    def ReadBytes(self):
        size = int.from_bytes(self.sock.recv(4), "big")
        return self.sock.recv(size)

    def SendFile(self, name):
        file_content = open(name,'rb').read()
        self.sock.send(len(file_content).to_bytes(4, byteorder='big'))
        self.sock.send(file_content)

    def GetFile(self, name, content):
        size = int.from_bytes(self.sock.recv(4), "big")
        open(name,'wb').write(self.sock.recv(size))

    def RemoveFile(self, name):
        os.remove(name)

    def run(self):
        while True:
            command = self.ReadData()
            command = command.Split()
            if command[0]=='getfile':
                SendFile(command[1])

            if command[0]=='sendfile':
                open(command[1],'wb').write(self.ReadBytes())

            if command[0]=='sendfilempty':
                open(command[1],'a').close()

            if command[0]=='remove':
                os.remove(command[1])

            if command[0]=='size':
                SendData(os.path.getsize(command[1]))


def AddFile(path, name):


def main():
    next_name = 1

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    sock.bind(('', 8080))
    sock.listen()
    
    while True:
        con, addr = sock.accept()
        clients.append(con)
        name = 'u' + str(next_name)
        next_name += 1
        
        print(str(addr) + ' connected as ' + name)

        ClientListener(name, con).start()
    


if __name__ == "__main__":
    main()