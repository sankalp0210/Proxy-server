from __future__ import print_function
import time
import os
import threading
import socket,sys
import signal
max_conn = 20
buffer_size = 4096
HOST = ""
PORT = 20100

def proxy_server(webserver,port,conn,addr,filename):
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.connect((webserver,port))
	print("=> Page:",filename)
	if filename in os.listdir('./.cache/'):
		s.send("GET /"+ filename + " HTTP/1.1\r\nIf-Modified-Since: " + time.ctime(os.path.getmtime('./.cache/' + filename)) + " \r\n\r\n")
	else:
		s.send("GET "+ filename + " HTTP/1.1\r\n\r\n")
	reply = s.recv(buffer_size)
	print("++>reply is\n",reply)
	if reply.find("200") >= 0:	
		f = open(os.path.join('./.cache/',filename),'wb')
		while 1:
			if(len(reply) > 0):
				f.write(reply)
				conn.send(reply)
				dar = float(len(reply))/1024
				print("=> Request done to:",str(addr[0]),"Response Size(KB):",dar)
				reply = s.recv(buffer_size)
			else: 
				break	
		f.close()		
	elif reply.find("304") >= 0:
		print("=> Response Code:304 Already present in cache")
		f = open(os.path.join('./.cache/',filename),'rb')		
		l = f.read(buffer_size)
		while (l):
	   		conn.send(l)
	   		l = f.read(buffer_size)
	   	f.close()	
	else:
		print("=> Response Status:",reply)			
	s.close()
	conn.close()

def conn_string(conn,addr,byte_data):
	try:
		data = str(byte_data)
		first_line = data.split('\r\n')[0]
		url = first_line.split()[1]
		http_pos = url.find('://')
		if(http_pos == -1):
			temp = url 
		else:
			temp = url[(http_pos+3):]
		port_pos = temp.find(':')
		webserver_pos = temp.find('/')
		if webserver_pos == -1:
			webserver_pos = len(temp)
		webserver = ''
		port = -1
		if port_pos == -1 or webserver_pos < port_pos:
			port = 80
			webserver = temp[:webserver_pos]
		else:
			port = int((temp[(port_pos+1):])[:webserver_pos - port_pos -1])
			webserver = temp[:port_pos]
		print("=> Request",webserver,port)    
		try:
			filename = temp.split('/')[1]
		except IndexError:
			filename = '/'
		proxy_server(webserver,port,conn,addr,filename)
	except Exception as e:
		print("Thread Creation Exception:",e)

def start():
	if os.path.isdir('./.cache'):
		print("Using the existing cache")
	else:
		os.makedirs('.cache')
		print("Creating folder .cache")	
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	s.bind((HOST, PORT))
	s.listen(max_conn)
	while True:
		try:
			(conn, addr) = s.accept() 
			data = conn.recv(buffer_size)
			t = threading.Thread(target=conn_string,args=(conn,addr,data))
			t.start()
		except Exception as e: 
			print("Proxy server Shutting down")
			print("Error:",e)
			s.close()
			sys.exit(1)
	s.close()    
if __name__ == '__main__':
	start()