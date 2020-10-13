import socket
import os
#import sys
from pythonping import ping
from threading import Thread
import os.path
import hashlib
from time import time
import pickle


SEPARATOR = "<SEPARATOR>"

clients = []

current_directory = '/'

storage_ips = sys.argv[1:]

class StorageCommander:
    def __init__(self):
        self.sock = socket.socket()
        self.ipstring = '34.66.53.161'
        self.sock.connect(('34.66.53.161',5000))

    def ChoseServer(self):
        if not ping(ipstring, size=40, count=1)._responses[0].success:
            for ip in storage_ips:
                if ping(ip, size=40, count=1)._responses[0].success:
                    self.sock.close()
                    self.sock.connect((ip, 5000))
                    ipstring = ip
                    return

storage = StorageCommander()

primary_storage_id = 0


class Node:
 
    def __init__(self, parent, name, isFile, file_content = None): # file_content - bytes, file name is sha256 of full path
        self.name = name
        self.parent = parent;
        self.isFile = isFile
        #self.fullpath = self.GetPath() + name
        self.lock = False
        if isFile:
            self.filename = hashlib.sha256(str(time()).encode()).hexdigest()
            self.children = None
            SendFileToStorage(self.filename, file_content)
            #open(self.filename, 'a').close()
        else:
            self.filename = None
            self.children = []
        pass

    def Rename(self, newname):
        self.name = newname
        #self.fullpath = self.GetPath() + newname

    def Move(self, move_to_node):
        if not self.isFile and self.isLock() or self.lock:
            return 0
        move_to_node.children.append(self)
        self.parent.children.remove(self)
        self.parent = move_to_node
        return 1

    def isLock(self):
        if isFile:
            return self.lock
        else:
            for child in self.children:
                if child.lock:
                    return True
        return False

    def Remove(self, node):
        if not self.isFile and self.isLock() or self.lock:
            return 0
        if node.children != None:
            for child in node.children:
                Remove(child)
        else:
            SendCommandToStorage('remove '+node.filename)
            #os.remove(node.filename)
        node.parent.children.remove(node)
        node.parent = None
        del node
        return 1

    def PrintTree(self, identation = 0):
        print(identation*' '+self.name)
        if self.children != None:
            for child in self.children:
                child.PrintTree(identation+4)

    def AddFile(self, name, content):
        self.children.append(Node(self, name, True, content))

    def AddDirectory(self, name):
        self.children.append(Node(self, name, False))

    @staticmethod
    def Root():
        return Node(None, '/', False)

    def Init(self):
        for child in self.children:
            if child.Remove()==0:
                return 0
        return 1

    def FindDirectory(self, name):
        for child in self.children:
            if(child.name == name and not child.isFile):
                return child
        return None

    def FindFile(self, name):
        if self.children != None:
            for child in self.children:
                if(child.name == name):
                    return child
        return None

    def SaveNode(self):
        pickle.dump(self, open('simple1.pkl', 'wb'))

    def FindPath(self, path):
        if len(path)>1:
            if path[0]=='..':
                nextdir = self.parent
            else:
                nextdir = self.FindDirectory(path[0])
            if nextdir!=None:
                return nextdir.FindPath(path[1:])
        else:
            if(path[0]==''):
                return self
            else:
                return self.FindDirectory(path[0])
        return None

    def Read(self):
        info = ''
        for child in self.children:
            if child.isFile:
                info.append(child.name+'(f)   ')
            else:
                info.append(child.name+'(d)   ')
        return info

    def OpenFile(self):
        return GetFile(self.filename)

    def GetPath(self):
        if(self.name == '/'):
            return '/'
        return parent.GetPath()+parent.name+'/'



def SendCommandToStorage(command):
    bytes_to_send = command.encode()
    storage.sock.send((len(bytes_to_send)).to_bytes(4,byteorder="big"))
    storage.sock.send(bytes_to_send)

def SendBytesToStorage(bytes_to_send):
    storage.sock.send((len(bytes_to_send)).to_bytes(4,byteorder="big"))
    storage.sock.send(bytes_to_send)

def SendFileToStorage(name, content):
    if content==None:
        SendCommandToStorage('sendfilempty '+name)
    else:
        SendCommandToStorage('sendfile '+name)
        SendBytesToStorage(content)

def GetFile(name):
    SendCommandToStorage('getfile '+name)
    size = int.from_bytes(storage.sock.recv(4), "big")
    return storage.sock.recv(size)

def GetSize(name):
    SendCommandToStorage('size '+name)
    size = int.from_bytes(storage.sock.recv(4), "big")
    return storage.sock.recv(size).decode()

# Thread to listen one particular client
class ClientListener(Thread):
    def __init__(self, name, sock, root):
        super().__init__(daemon=True)
        self.sock = sock
        self.name = name
        self.root = root
    # clean up
    def _close(self):
        #print("HERE")
        clients.remove(self.sock)
        self.sock.close()
        print(self.name + ' disconnected')

    def ReadData(self):
        size = int.from_bytes(self.sock.recv(4), "big")
        return self.sock.recv(size).decode()

    def ReadBytes(self):
        size = int.from_bytes(self.sock.recv(4), "big")
        return self.sock.recv(size)

    def SendData(self, data_string):
        self.sock.send(len(data_string).to_bytes(4, byteorder='big'))
        self.sock.send(data_string.encode())

    def Error(self):
        self.SendData('Error')

    def run(self):
        while True:
            data = self.ReadData()
            command = data[0]
            if command=='mkfile':
                path = data[1]
                directory_path = os.path.dirname(path)
                file_name = os.path.basename(path)
                directory = self.root.FindPath(directory_path.split('/')[1:])
                if directory!=None:
                    directory.AddFile(file_name, None)
                    self.SendData(file_name)
                else:
                    self.Error()
                continue

            if command=='mkdir':
                path = data[1]
                parent_path = os.path.dirname(path)
                name = os.path.basename(path)
                directory = self.root.FindPath(parent_path.split('/')[1:])
                if directory!=None:
                    directory.AddDirectory(name)
                    self.SendData(name)
                else:
                    self.Error()
                continue

            if command=='init':
                if self.root.Init()==1:
                    self.SendData('Successful Init')
                else:
                    self.Error()
                continue

            if command=='cd':
                path = data[1]
                if self.root.FindPath(path.split('/')[1:])!=None:
                    self.SendData(os.path.basename(path))
                else:
                    self.Error()
                continue

            if command=='ls':
                path = data[1]
                directory = self.root.FindPath(path.split('/')[1:])
                if directory!=None:
                    self.SendData(directory.Read())
                else:
                    self.Error()
                continue

            if command=='cat':
                path = data[1]
                directory_path = os.path.dirname(path)
                file_name = os.path.basename(path)
                directory = self.root.FindPath(directory_path.split('/')[1:])
                if directory==None:
                    self.Error()
                    continue
                file_node = directory.FindFile(file_name)
                if file_node!=None:
                    self.SendData(file_node.OpenFile())
                else:
                    self.Error()
                continue

            if command=='send':
                path = data[1]
                directory_path = os.path.dirname(path)
                file_name = os.path.basename(path)
                directory_node = self.root.FindPath(directory_path.split('/')[1:])
                if directory_node!=None:
                    self.SendData('Directory found')
                else:
                    self.Error()
                    continue
                directory_node.AddFile(file_name, self.ReadBytes())
                self.SendData(file_name)
                continue

            if command=='cp':
                args = data[1:]
                directory_path = os.path.dirname(path[0])
                file_name = os.path.basename(path[0])
                target_directory = path.arg[1]
                from_node = self.root.FindPath(directory_path.split('/')[1:])
                if from_node!=None:
                    file_node = from_node.FindFile(file_name)
                    to_node = self.root.FindPath(target_directory.split('/')[1:])
                    if file_node!=None and to_node!=None:
                        to_node.AddFile(file_name, file_node.OpenFile())
                        self.SendData(file_name)
                        continue
                self.Error()
                continue

            if command=='mv':
                args = data[1:]
                directory_path = os.path.dirname(path[0])
                file_name = os.path.basename(path[0])
                target_directory = path.arg[1]
                from_node = self.root.FindPath(directory_path.split('/')[1:])
                if from_node!=None:
                    file_node = from_node.FindFile(file_name)
                    to_node = self.root.FindPath(target_directory.split('/')[1:])
                    if file_node!=None and to_node!=None:
                        file_node.Move(to_node)
                        self.SendData(file_name)
                        continue
                self.Error()
                continue

            if command=='info':
                path = data[1]
                directory_path = os.path.dirname(path)
                file_name = os.path.basename(path)
                directory = self.root.FindPath(directory_path.split('/')[1:])
                if directory==None:
                    self.Error()
                    continue
                file_node = directory.FindFile(file_name)
                if file_node!=None:
                    self.SendData('Full Path: '+os.path.splitext(path)[0]+
                        '\nExtention: '+os.path.splitext(path)[1]+
                        '\nSize(bytes): '+GetSize(file_node.filename)+
                        '\nContent file name: '+file_node.filename)
                else:
                    self.Error()
                continue

            if command=='delfile':
                path = data[1]
                directory_path = os.path.dirname(path)
                file_name = os.path.basename(path)
                directory = self.root.FindPath(directory_path.split('/')[1:])
                if directory==None:
                    self.Error()
                    continue
                file_node = directory.FindFile(file_name)
                if file_node!=None:
                    self.SendData(file_name)
                    file_node.Remove()
                else:
                    self.Error()
                continue

            if command=='deldir':
                path = data[1]
                directory = self.root.FindPath(path.split('/')[1:])
                if directory!=None:
                    directory.Remove()
                    self.SendData(os.path.basename(path))
                else:
                    self.Error()
                continue

def main():
    print('root')
    root = Node.Root()
    print('rooted')
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
        storage.ChoseServer()
        ClientListener(name, con, root).start()


if __name__ == "__main__":
    main()