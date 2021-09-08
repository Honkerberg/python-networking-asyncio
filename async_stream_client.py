import socket
import time
import asyncio

# Connection config constants
HOST = '127.0.0.1'
PORT = 20001
NEW_LINE = '\r\n' # Used when you send data(\r\n = Carriage return + Line feed)


year = int(time.strftime("%Y"))
month = time.strftime("%m")
day = time.strftime("%d")
hour = time.strftime("%H")
minute = time.strftime("%M")
second = time.strftime("%S")

# Dictionary with messages you can send
orders = {
    "status":
        f"Status("
            "MessId 'nr', "
            "AckMessId 'nr', "
            "Info All/Teach/Device, "
            "Tray 'nr'/All, "
            "OrderQueue 'nr'/All, "
            "ExtAck 'transId')"
    ,
    "statusall": # Derived message from status above
        f"Status("
            "MessId {}, "
            "AckMessId {}, "
            "Info Device)"
    ,
    "fetchtray":
        f"FetchTray("
            "MessId 'nr', "
            "TransID 'nr', "
            "Opening 'nr', "
            "Start 0/1, "
            "Type Out/In/OutNoReturn/InNoReturn, "
            "Tray 'nr', "
            "Box 'Position', "
            "ArtNr 'Number', "
            "ArtText 'Text')"
    ,
    "fetchpriotray":
        f"FetchPrioTray("
            "MessId 'nr', "
            "TransID 'nr', "
            "Opening 'nr', "
            "Start 0/1, "
            "Type Out/In/OutNoReturn/InNoReturn, "
            "Tray 'nr', "
            "Box 'Position', "
            "ArtNr 'Number', "
            "ArtText 'Text')"
    ,
    "nexttray":
        f"NextTray("
            "MessId 'nr', "
            "Opening 'nr', "
            "Tray1 'nr', "
            "Tray2 'nr', "
            "Tray3 'nr')"
    ,
    "openinvent":
        f"OpenInvent("
            "MessId 'nr', "
            "Opening 'nr', "
            "TransId 'nr', "
            "Enable '1' or '0')"
    ,
    "eraseorderqueue":
        f"EraseOrderQueue("
            "MessId 'nr', "
            "Opening 'nr' or Opening All)"
    ,
    "writerow":
        f"WriteRow("
            "MessId 'nr', "
            "Opening 'nr', "
            "Text 'text')"
    ,
    "lightbar":
        f"LightBar("
            "MessId 'nr', "
            "Opening 'nr', "
            "Type 'nr', "
            "XPos 'nr', "
            "XSize 'nr', "
            "YDigit 'nr')"
    ,
    "laserpointer":
        f"LaserPointer("
            "MessId 'nr', "
            "LpId 'nr', "
            "Type 'nr', "
            "XPos 'nr', "
            "YPos 'nr')"
    ,
    "sidetable":
        f"SideTable("
            "MessId 'nr', "
            "Opening 'nr', "
            "Type 'Out/In', "
            "XPos 'nr')"
    ,
    "settime":
        f"SetTime("
            "MessId {}, "
            "Year {}, "
            "Month {}, "
            "Day {}, "
            "Hour {}, "
            "Minute {}, "
            "Second {})"
    ,
    "ton":
        f"Ton"
    ,
    "toff":
        f"Toff"
    ,
}

with socket.socket(socket.AF_INET,socket.SOCK_STREAM) as s:
        nr = 1

        async def connection():
            try:
                print("Connecting...")
                await asyncio.sleep(2)
                s.connect((HOST, PORT))
                print("Connected successfully, communication begins..")
                await asyncio.sleep(1)

            except socket.error as exc:
                print("Exception caught: %s" % exc)
        
        async def set_time(nr):
            timeinfo = (orders["settime"].format(nr, year, month, day, hour, minute, second)) + NEW_LINE
            s.send(timeinfo.encode())
            data_time = s.recv(1024)
            print(data_time.decode())
            print("Actual date time set.")
            await asyncio.sleep(1)

        # FetchTray, NextTray, WriteRow.. - these send in this order
        async def send_message_status(nr):
            message = orders["statusall"].format(nr, nr) + NEW_LINE
            s.send(message.encode())
            data = s.recv(1024)
            print(data.decode())
            await asyncio.sleep(1)

        # Preparation for async communication
        # Main function for calling async functions declared above

        async def main(nr):
            print(f"Main function started at {time.strftime('%X')}")
            task1 = asyncio.create_task(connection())
            await task1
            task2 = asyncio.create_task(set_time(nr))
            await task2
            task3 = asyncio.create_task(send_message_status(nr))
            await task3
            print(f"Main function completed at {time.strftime('%X')}")

        asyncio.run(main(nr))
        # set_time()
        # send_message()
