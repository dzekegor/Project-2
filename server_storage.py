import socket
import os
from threading import Thread
import os.path
import hashlib
from time import time
import pickle


SEPARATOR = "<SEPARATOR>"

clients = []

current_directory = '/'

files = []

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
            if file_content != None:
                f = open(self.filename, "wb")
                f.write(file_content)
                files.append(self.filename)
                f.close()
            else:
                open(self.filename, 'a').close()
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
            os.remove(node.filename)
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
            if nextdir!=None
                return nextdir.FindPath(path[1:])
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
        return open(self.filename, 'rb').read()

    def GetPath(self):
        if(self.name == '/'):
            return '/'
        return parent.GetPath()+parent.name+'/'


# Thread to listen one particular client
class ClientListener(Thread):
    def __init__(self, name: str, sock: socket.socket, root):
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

    def Error(self):
        self.SendData('Error'.encode())

    def run(self):
        while True:
            command = self.ReadData()
            if command=='mkfile':
                path = self.ReadData()
                directory_path = os.path.dirname(path)
                file_name = os.path.basename(path)
                directory = root.FindPath(directory_path.split('/')[1:])
                if directory!=None:
                    directory.AddFile(file_name, None)
                    self.SendData(file_name.encode())
                else:
                    self.Error()
                continue

            if command=='mkdir':
                path = self.ReadData()
                parent_path = os.path.dirname(path)
                name = os.path.basename(path)
                directory = root.FindPath(parent_path.split('/')[1:])
                if directory!=None:
                    directory.AddDirectory(name)
                    self.SendData(name.encode())
                else:
                    self.Error()
                continue

            if command=='init':
                if root.Init()==1:
                    self.SendData("Successful Init")
                else:
                    self.Error()
                continue

            if command=='cd':
                path = self.ReadData()
                if root.FindPath(path.split('/')[1:])!=None:
                    self.SendData(os.path.basename(path).encode())
                else:
                    self.Error()
                continue

            if command=='ls':
                path = self.ReadData()
                directory = root.FindPath(path.split('/')[1:])
                if directory!=None:
                    self.SendData((directory.Read()).encode())
                else:
                    self.Error()
                continue

            if command=='cat':
                path = self.ReadData()
                directory_path = os.path.dirname(path)
                file_name = os.path.basename(path)
                directory = root.FindPath(directory_path.split('/')[1:])
                if directory==None:
                    self.Error()
                    continue
                file_node = directory.FindFile(file_name)
                if file_node!=None:
                    self.SendData(file_node.OpenFile())
                else:
                    self.Error()
                continue




def main():
    root = Node.Root()
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

        ClientListener(name, con, root).start()
    


if __name__ == "__main__":
    main()