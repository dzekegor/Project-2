import socket
import os
from threading import Thread
import sys
import os.path


SEPARATOR = "<SEPARATOR>"

clients = []
files = {}
lastfilename = ""

class Replicator:
    def __init__(self):
        self.isPrimary = False
    
    def SetSiblings(self, siblings):
        self.isPrimary = True
        self.sibling_ips = siblings
        self.sockets = []
        for ip in siblings:
            s = socket.socket()
            s.connect((ip, 5000))
            self.sockets.append(s)
            
    def Replicate(self, name):
        if not self.isPrimary:
            return
        for sock in self.sockets:
            self.SendCommand(sock, 'sendfile '+name)
            self.SendFile(sock, name)
            
    def ReplicateEmpty(self, name):
        if not self.isPrimary:
            return
        for sock in self.sockets:
            self.SendCommand(sock, 'sendfilempty '+name)
            
    def Remove(self, name):
        if not self.isPrimary:
            return
        for sock in self.sockets:
            self.SendCommand(sock, 'remove '+name)
            
    def SendFile(self, sock, name):
        bytes_to_send = open(name,'rb').read()
        count = len(bytes_to_send)//1024
        rem = len(bytes_to_send)%1024
        if rem >0:
            count+=1
        sock.send(count.to_bytes(4,byteorder="big"))
        sock.send(rem.to_bytes(4,byteorder="big"))
        for i in range(count):
            sock.send(bytes_to_send[1024*i:1024*(i+1)])
      
    def SendCommand(self, sock, command):
        bytes_to_send = command.encode()
        sock.send((len(bytes_to_send)).to_bytes(4,byteorder="big"))
        sock.send(bytes_to_send)
            
        
    
replicator = Replicator()
    
# Thread to listen one particular client
class ClientListener(Thread):
    def __init__(self, name: str, sock: socket.socket):
        super().__init__(daemon=True)
        self.sock = sock
        self.name = name
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
        count = int.from_bytes(self.sock.recv(4), "big")
        last_size = int.from_bytes(self.sock.recv(4), "big")
        result = b''
        for i in range(count):
            if i==count-1:
                if last_size==0:
                    result+=self.sock.recv(1024)
                else:
                    result+=self.sock.recv(last_size)
            else:
                result+=self.sock.recv(1024)
        print(result)
        return result

    def SendFile(self, name):
        bytes_to_send = open(name,'rb').read()
        count = len(bytes_to_send)//1024
        rem = len(bytes_to_send)%1024
        if rem >0:
            count+=1
        self.sock.send(count.to_bytes(4,byteorder="big"))
        self.sock.send(rem.to_bytes(4,byteorder="big"))
        for i in range(count):
            self.sock.send(bytes_to_send[1024*i:1024*(i+1)])

    def GetFile(self, name, content):
        size = int.from_bytes(self.sock.recv(4), "big")
        open(name,'wb').write(self.sock.recv(size))

    def RemoveFile(self, name):
        os.remove(name)

    def run(self):
        while True:
            command = self.ReadData()
            command = command.split()
            if command[0]=='siblings':
                replicator.SetSiblings(command[1:])

            if command[0]=='getfile':
                self.SendFile(command[1])

            if command[0]=='sendfile':
                open(command[1],'wb').write(self.ReadBytes())
                replicator.Replicate(command[1])

            if command[0]=='sendfilempty':
                open(command[1],'a').close()
                replicator.ReplicateEmpty(command[1])

            if command[0]=='remove':
                os.remove(command[1])
                replicator.Remove(command[1])

            if command[0]=='size':
                self.SendData(str(os.path.getsize(command[1])))


def main():
    next_name = 1
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(('', 5000))
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
