import os
import time
import base64
import datetime
import socket
import threading
import SocketServer
import sys
import SimpleHTTPServer

BLACKLIST = "block.txt"
AUTHFILE = "auth.txt"
BUFFER_SIZE = 1024

class server():

    def __init__(self):
        self.blocked = []
        self.cache = {}
        self.users = []
        self.count_occurance = dict()
        if os.path.isdir('./.cache'):
            print("Using the existing cache")
        else:
            os.makedirs('.cache')
            print("Creating folder .cache")
        try:
            self.sock = socket.socket()
            self.sock.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR, 1)
            self.sock.bind(('', 20100))
            self.sock.listen(10)
        
        except (KeyboardInterrupt, SystemExit):
            raise
        
        except:
            print "Cannot initialise"

    def set_interval(self,func, sec):
        def func_wrapper():
            self.set_interval(func, sec)
            func()
        t = threading.Timer(sec, func_wrapper)
        t.start()
        return t
        
    def clear(self):
        self.count_occurance = {}
        self.cache = {}       
    
    def postreq(self,host,port,request,conn):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # s.settimeout(50)
            s.connect((host, port))
            s.sendall(request)

            while True:
                data = s.recv(BUFFER_SIZE)
                if len(data) > 0 :
                    conn.send(data)
                else:
                    break
        except (KeyboardInterrupt, SystemExit):
            raise
        except Exception as e:
            s.close()
            conn.close()
            print e
            sys.exit(0)
        
    def getreq(self,host,port,request,conn,filen):
        url = request.splitlines()[0].split(' ')[1]
        filename = url.replace("/",";")
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((host, port))
            # s.sendall(request)
            if filename in os.listdir('./.cache'):
                # s.send("GET "+ url + " HTTP/1.1\r\nIf-Modified-Since: " + time.ctime(os.path.getmtime('./.cache/' + filename)) + " \r\n\r\n")
                # request = request.splitlines()[0] + 'If-Modified-Since: ' + time.ctime(os.path.getmtime('./.cache/' + filename)) + '\r\n\r\n'
                tobesent = request.split("\r\n")
                while tobesent[len(tobesent)-1] == '':
                    tobesent.remove('')
                tm = time.ctime(os.path.getmtime('./.cache/' +filename))
                bt = os.path.getmtime('./.cache/' +filename)
                tme = str(datetime.datetime.utcfromtimestamp(bt))
                tme = tme.split(' ')[1].split('.')[0]
                tm = tm.split(' ')
                tm.remove('')
                day = tm[0]
                month = tm[1]
                date = tm[2]
                # tme = tm[3]
                year = tm[4]
                # print tm
                header = "If-Modified-Since: " + day + ", " + date + " " + month + " " + year + " " + tme + " GMT"
                # header = "If-Modified-Since: " + "Wed, 03 Apr 2019 15:00:00 GMT"
                tobesent.append(header)
                request = "\r\n".join(tobesent) + "\r\n\r\n"
            print request
            s.sendall(request)
            data = s.recv(BUFFER_SIZE)
            
            if data.splitlines()[0].find("200") != -1:
                print("without using cache")
                if host in self.count_occurance:
                    self.count_occurance[host] += 1
                else:
                    self.count_occurance[host] = 1
                flag = False        
                if self.count_occurance[host]>=3:
                    flag = True
                if flag:
                    file = open('./.cache/' + filename,'w+')
                    # file = open(os.path.join('./.cache/',filename),'w+')
                while len(data):
                    conn.send(data)
                    if flag: 
                        file.write(data)
                    data = s.recv(BUFFER_SIZE)
                if flag:
                    file.close()

            elif data.splitlines()[0].find("304") != -1:
                print ("304:Using Cache")
                file = open(os.path.join('./.cache/',filename),'rb')
                l = file.read(BUFFER_SIZE)
                while(l):
                    conn.send(l)
                    l = file.read(BUFFER_SIZE)
                file.close()
            else:
                print "==>>Response ", data
        
        except (KeyboardInterrupt, SystemExit):
            raise
        
        except Exception as e:
            print e
            sys.exit(0)
        s.close()

    def serve_request(self, conn, addr):
        request = conn.recv(BUFFER_SIZE)
        lines = request.splitlines()
        # print request
        if len(lines) == 0 :
            return
        auth_line = [ line for line in lines if "Authorization" in line]
        if len(auth_line):
            auth_line = auth_line[0].split(' ')[2]
        else:
            auth_line = None
        method = lines[0].split(' ')[0]
        url = lines[0].split(' ')[1]
        # print url
        pos_port = url.find(':',5,len(url))
        file_pos = url.find('/',8,len(url))
        filename = 'bt' + url[file_pos+1:].split('/')[0]
        host = lines[1].split(' ')[1]
        if pos_port == -1:
            port = 80
        else :
            port = url[pos_port+1:]
            port = int(port[:len(port)-1])
        blckflag = False
        if host in self.blocked and auth_line not in self.users:
            blckflag = True
        if blckflag:
            print "The given Hostname:%s is blocked for you.For further details contact your ISP" % host
            conn.send("HTTP/1.0 200 OK\r\nContent-Length: 22\r\n\r\nWebsite is Blocked\r\n\r\n")
        elif method == "POST":
            self.postreq(host,port,request,conn)
        elif method == "GET":
            self.getreq(host,port,request,conn, filename)

        conn.close()

    def begin(self):
        # try:
        #     self.set_interval(self.clear,5*60)
        # except (KeyboardInterrupt, SystemExit):
        #     sys.exit(0)
        while True:
            try:
                conn, addr = self.sock.accept()
                thread = threading.Thread(target=self.serve_request, args=(conn, addr))
                thread.setDaemon(True)
                thread.start()
            except (KeyboardInterrupt, SystemExit):
                raise
            except:
                print "Could not accept request"

ser = server()
# reading and storing blacklisted URL's
file = open(BLACKLIST,"rb")
data = ""
chunks = file.read()
while chunks:
    data += chunks
    chunks = file.read()
file.close()
ser.blocked = data.splitlines()

# reading and storing username and passwords
file = open(AUTHFILE,"rb")
data = ""
chunks = file.read()
while chunks:
    data += chunks
    chunks = file.read()
file.close()
data = data.splitlines()
for d in data:
    ser.users.append(base64.b64encode(d))
ser.begin()
