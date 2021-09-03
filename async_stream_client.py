import socket
import asyncio
import time


# Connection config
HOST = '127.0.0.1'
PORT = 20001
NEW_LINE = '\r\n' # Must be used at every message when you need send data to PLC (\r a \n - CR LF (Carriage return + Line feed))

with socket.socket(socket.AF_INET,socket.SOCK_STREAM) as s:


        def connection():
            s.connect((HOST, PORT))
            print('Connected successfully!')

        def send_message():
            message = "Status( MessId '1', AckMessId '1', Info Device)" + NEW_LINE
            s.send(message.encode())
            data = s.recv(1024)
            print(data.decode())

        def set_time():
            timeinfo = "SetTime( MessId '2', Year 2021, Month 9, Day 3, Hour 10, Minute 15, Second 0)" + NEW_LINE
            s.send(timeinfo.encode())
            data_time = s.recv(1024)
            print(data_time.decode())
            print('Date time set.')

        connection()
        send_message()
        set_time()

