# # Import socket module 
# import socket                
# import time  
# import ast
# # Create a socket object 
# # s = socket.socket()
# s = socket.socket(socket.AF_INET, # Internet
#                   socket.SOCK_DGRAM) # UDP   
  
# # Define the port on which you want to connect 
# port = 27015                
# print('start')
# # connect to the server on local computer 
# s.connect(('1810-ST-57V36P2', port)) 
# # s.connect(('127.0.0.1', port)) 
# # while True:
# #     pass  
# # receive data from the server 
# print('connected')
# HOST = '1810-ST-57V36P2'    # The remote host
# PORT = 27015              # The same port as used by the server
# s.connect((HOST, PORT))

# try:
#     while True:
#         print('recv')
#         # try:
#         print(s.recv(1024).decode("utf-8"))
#         # except KeyboardInterrupt:
#         #     break
#         # except:
#         #     pass
#         time.sleep(1)
# except KeyboardInterrupt:
#     print('ending')
# # close the connection 
# s.close()

import socket
import sys

HOST = ''    # The remote host
PORT = 27014              # The same port as used by the server
s = None
i = 0
for res in socket.getaddrinfo(HOST, PORT, 0, 0, socket.IPPROTO_UDP):
    af, socktype, proto, canonname, sa = res
    print(af, socktype, proto, canonname, sa)
 
# try:
#     while True:
#         print('recv')
#         # try:
#         print(s.recv(1024).decode("utf-8"))
#         # except KeyboardInterrupt:
#         #     break
#         # except:
#         #     pass
#         time.sleep(1)
# except KeyboardInterrupt:
#     print('ending')
# # close the connection 
# s.close()

PORT = 27014              # The same port as used by the server
s = None
s = socket.socket(2, 2, 0)
s.bind(("127.0.0.1", PORT))
# s.connect(("127.0.0.1", PORT))
# s.connect(('1810-ST-57V36P2', PORT))
print('opened socket')
s.settimeout(3.0)
data = s.recv(1024)
s.setblocking(True)
while True:
    try:
        data = s.recv(1024)
        print('Received', str(data.decode("utf-8", errors='ignore')).split('\0')[0])
    except KeyboardInterrupt:
        sys.exit(1)
s.close()
