import os
import time
import socket
import threading
import SocketServer
import sys
import SimpleHTTPServer

class server():

    def __init__(self):
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
            s.settimeout(50)
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
        
    def getreq(self,host,port,request,conn):
        
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(50)
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

    def serve_request(self, conn, addr):
        request = conn.recv(262144)
        lines = request.splitlines()
        print request
        if len(lines) == 0 :
            pass
        method = lines[0].split(' ')[0]
        url = lines[0].split(' ')[1]
        pos_port = url.find(':',5,len(url))
        host = lines[1].split(' ')[1]
        if pos_port == -1:
            port = 80
        else :
            port = url[pos_port+1:]
            port = int(port[:len(port)-1])

        if method == "POST" :
            self.postreq(host,port,request,conn)

        elif method == "GET":
            self.getreq(host,port,request,conn)    
    
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
