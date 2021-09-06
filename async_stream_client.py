import socket
import time
import asyncio

# Connection config constants
HOST = '127.0.0.1'
PORT = 20001
NEW_LINE = '\r\n' # Must be used at every message when you need send data to PLC (\r a \n - CR LF (Carriage return + Line feed))

with socket.socket(socket.AF_INET,socket.SOCK_STREAM) as s:


        async def connection():
            try:
                print('Connecting...')
                await asyncio.sleep(2)
                s.connect((HOST, PORT))
                print('Connected successfully, communication begins..')
                await asyncio.sleep(3)

                while True:
                    data = s.recv(1024)
                    if not data:
                        print('Connection automatically ended.')
                        break

            except socket.error as exc:
                print("Exception caught: %s" % exc)


        def send_message():
            message = "Status( MessId '1', AckMessId '1', Info Device)" + NEW_LINE
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


        # Preparation for async communication
        # Main function for calling async functions
        async def main(): 
            task1 = asyncio.create_task(connection())

        asyncio.run(connection())

        # asyncio.run(main())
        # set_time()
        # send_message()