import socket

# Connection config
HOST = '127.0.0.1'
PORT = 20001

with socket.socket(socket.AF_INET,socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    data = 'Help' + '\r' + '\n' # Vzdy pouzit \r a \n - CR LF (Carriage return + Line feed)
    s.send(data.encode())
    serverdata = s.recv(1024)
    print(serverdata.decode())