import os
import socket

host = "104.197.214.149"
port = 8080

addr = (host, port)
sock = socket.socket()

print(f"[+] Connecting to {host}:{port}")

sock.connect(addr)

print("[+] Connected.")

def send(msg):
    sock.send((len(msg)).to_bytes(4,byteorder="big"))
    sock.send(bytes(msg.encode("utf-8")))
    size = int.from_bytes(sock.recv(4),byteorder="big")
    data = sock.recv(size)
    return data.decode("utf-8")

def lexer(c):
    lex=''
    arg=''
    l=True
    for i in c:
        if i==' ' and l:
            l=False
        elif l:
            lex+=i 
        else:
            arg+=i
    return shell(lex,absolutize(arg))

cur_dir = "/"
    
def absolutize(arg):
    if arg == "":
        return cur_dir
    if arg == "..":
        if "/".join(cur_dir.split("/")[:-2]) == "":
            return "/"
        return "/".join(cur_dir.split("/")[:-2])
    if arg[0:2] == "..":
        arg = "/".join(cur_dir.split("/")[:-2]) + arg[2:]
    if arg[0] == ".":
        arg = cur_dir + arg[2:]
    if arg[0] != "/":
        arg = cur_dir + arg
    if arg[-1] == "/":
        arg = arg[:-1]
    return arg
def shell(lex,arg):
    global cur_dir
    if lex=='exit': 
        return True
    elif lex=='cd': # Open directory
        if arg != "":
            res = send(lex+' '+arg)
            if res != "Error":
                
                if arg[-1] != "/":
                    arg = arg + "/"
                cur_dir = arg
            print(res)
    elif lex=='mkfile': # Create file
        if arg != "":
            res = send(lex+' '+arg)
            print(res)
    elif lex=='mkdir': # Create directory
        if arg != "":
            res = send(lex+' '+arg)
            print(res)
        else:
            print("Error")
    elif lex=='ls': # Read directory
        res = send(lex+' '+arg)
        print(res)
    elif lex=='init': # Initialize
        res = send(lex)
        print(res)
    elif lex=='cat': # Read file
        msg = lex+' '+arg
        sock.send((len(msg)).to_bytes(4,byteorder="big"))
        sock.send(bytes(msg.encode("utf-8")))
        count = int.from_bytes(sock.recv(4), "big")
        last_size = int.from_bytes(sock.recv(4), "big")
        result = b''
        for i in range(count):
            if i==count-1:
                if last_size==0:
                    result+=sock.recv(1024)
                else:
                    result+=sock.recv(last_size)
            else:
                result+=sock.recv(1024)
        print(result.decode("utf-8"))
        
    elif lex=='send': # Send file
        arg = arg.split(" ")
        f = open(arg[0],"rb").read()
        res = send(lex+' '+arg[1])
        print(res)
        p_number = len(f)//1024
        if len(f) % 1024 > 0:
            p_number += 1
        
        sock.send((p_number).to_bytes(4,byteorder="big"))
        if len(f) % 1024 != 0:
            sock.send((len(f) % 1024).to_bytes(4,byteorder="big"))
        else:
            sock.send((1024).to_bytes(4,byteorder="big"))
        f = open(arg[0],"rb")
        for i in range(p_number):
            sock.send(f.read(1024))
        size = int.from_bytes(sock.recv(4),byteorder="big")
        data = sock.recv(size)
        print(data.decode("utf-8"))
    elif lex=="cp": # Copy file
        res = send(lex+' '+arg)
        print(res)
    elif lex=="info": # File info
        res = send(lex+' '+arg) 
        print(res)
    elif lex=="mv": # Move file
        res = send(lex+' '+arg) 
        print(res)
    elif lex=="delfile": # Delete file
        res = send(lex+' '+arg) 
        print(res)
    elif lex=="deldir": # Delete dir
        res = send(lex+' '+arg) 
        print(res)
while True: 
    com=input(cur_dir.split("/")[-2]+"$ ")
    if lexer(com): break 
