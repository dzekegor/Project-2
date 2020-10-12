import socket
import os
from threading import Thread
import sys
import os.path


SEPARATOR = "<SEPARATOR>"

clients = []
files = {}
lastfilename = ""

#storage_ips = sys.argv[1:]


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

    def run(self):
        while True:
            command = self.ReadData()
            splited = command.split()
            operator = splited[0]
            arg = splited[1:]
            if operator=='mkfile':
                dir_path = os.path.dirname(arg[0])
                filename = os.path.basename(arg[0])
                storage = GetPrimaryStorage()
                SendDataToServer(storage, operator.encode())
                SendDataToServer(storage, arg[0].encode())



def GetPrimaryStorage():
    return storage_ips[0]
            
def SendDataToServer(storage_ip, data_bytes):
    s = socket.socket()
    s.connect(storage_ip, 5000)
    s.send(len(data_bytes).to_bytes(4, byteorder='big'))
    s.send(data_bytes)
    s.close()

def ReadData():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(('', 5000))
    s.listen()
    con, addr = s.accept()
    size = int.from_bytes(s.recv(4), "big")
    return s.recv(size).decode()

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