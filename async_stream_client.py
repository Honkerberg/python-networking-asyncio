import socket
import time
import asyncio


# Connection config
HOST = '127.0.0.1'
PORT = 20001
NEW_LINE = '\r\n' # Must be used at every message when you need send data to PLC (\r a \n - CR LF (Carriage return + Line feed))

with socket.socket(socket.AF_INET,socket.SOCK_STREAM) as s:


        def connection():
            s.connect((HOST, PORT))
            print('Connected successfully!')

        def send_message():
            # message = "Status( MessId '1', AckMessId '1', Info Device)" + NEW_LINE
            message = "Status(OrderQueue All)" + NEW_LINE # Sending messages without mess id?
            s.send(message.encode())
            data = s.recv(1024)
            print(data.decode())

        def set_time():
            year = time.strftime('%Y')
            month = time.strftime('%m')
            day = time.strftime('%d')
            hour = time.strftime('%H')
            minute = time.strftime('%M')
            second = time.strftime('%S')

            timeinfo = "SetTime(MessId '2', Year {0}, Month {1}, Day {2}, Hour {3}, Minute {4}, Second {5})" + NEW_LINE
            timeinfo = timeinfo.format(year, month, day, hour, minute, second)
            s.send(timeinfo.encode())
            data_time = s.recv(1024)
            print(data_time.decode())
            print('Date time set.')

        connection()
        set_time()
        send_message()