import os
import time
import socket
import threading
import SocketServer
import sys
import SimpleHTTPServer

class server():

    def __init__(self):
        self.cache = {}
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
    
    def postreq(self,host,port,request,conn):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # s.settimeout(50)
            s.connect((host, port))
            s.sendall(request)

            while True:
                data = s.recv(262144)
                if len(data) > 0 :
                    conn.send(data)
                else:
                    break

        except Exception as e:
            s.close()
            conn.close()
            print e
            sys.exit(0)
        
    def getreq(self,host,port,request,conn,filename):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # s.settimeout(50)
            s.connect((host, port))
            s.sendall(request)
            data = s.recv(262144)
            # print data
            if data.splitlines()[0].find("200"):
                print ("bt")
                file = open(os.path.join('./.cache/',filename),'wb')
                while len(data):
                    file.write(data)
                    conn.send(data)
                    data = s.recv(262144)
                file.close()
            elif data.splitlines()[0].find("304"):
                print ("304:Using Cache")
                file = open(os.path.join('./.cache/',filename),'rb')
                l = file.read(262144)
                while(l):
                    conn.send(l)
                    l = file.read(262144)
                file.close()
            else:
                print "==>>Response ", data

        except Exception as e:
            print e
            sys.exit(0)
        s.close()

    def serve_request(self, conn, addr):
        request = conn.recv(262144)
        lines = request.splitlines()
        # print request
        if len(lines) == 0 :
            return
        method = lines[0].split(' ')[0]
        url = lines[0].split(' ')[1]
        pos_port = url.find(':',5,len(url))
        file_pos = url.find('/',8,len(url))
        filename = 'bt' + url[file_pos+1:].split('/')[0]
        # print filename
        # print "file\n\n\n\n"
        host = lines[1].split(' ')[1]
        if pos_port == -1:
            port = 80
        else :
            port = url[pos_port+1:]
            port = int(port[:len(port)-1])

        if method == "POST" :
            self.postreq(host,port,request,conn)

        elif method == "GET":
            self.getreq(host,port,request,conn,filename)    

        conn.close()

    def begin(self):	
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
ser.begin()
