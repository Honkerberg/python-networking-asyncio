import socket
import time
import asyncio
import sys

# Connection config constants
HOST = "127.0.0.1"
PORT = 20001
NEW_LINE = "\r\n" # Used when you send data(\r\n = Carriage return + Line feed)

# Defined actual date time
year = time.strftime("%Y")
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
    "statusdevice": # Derived message from status above
        f"Status("
            "MessId {}, "
            "Info Device)"
    ,
    "statusqueueall": # Status queue all
        f"Status("
            "MessId {}, "
            "OrderQueue All)"
    ,
    "statusinfoall":  # Status info all
    f"Status("
        "MessId {}, "
        "Info All)"
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
    "fetchspecifictray": # Derived from fetchtray, add Count later
        f"FetchTray("
            "MessId {}, "
            "TransId {}, "
            "Opening 1, "
            "Start 1, " # 0 or 1
            "Type OutNoReturn, " # In/Out/OutNoReturn/InNoReturn
            "Tray {}, "
            "Box {}, " # Box position
            "Count {}, "
            "ArtNr {}, " # Article number (text or number?)
            "ArtText {} )" # Description of items on tray - Article text
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
    sys.stdout.flush()
    artnr = 'Test artiklu'
    textarg = 'Toto je popis k artiklu.'
    format_artnr = "< {}>".format(len(artnr)) + artnr
    format_textarg = "< {}>".format(len(textarg)) + textarg
    box_position = 2
    tray = 10
    count = 23
    transID = 101
    nr = 1

    async def connection():
        try:
            print("Connecting...")
            await asyncio.sleep(1.5)
            s.connect((HOST, PORT))
            print("Connected successfully, communication begins..")
            await asyncio.sleep(1)
            
        except:
            print("Connection error.")

    async def message_generator(nr, message):
        s.send(message.encode())
        if "SetTime" in message:
            print("Date time set.")
        elif "OrderQueue All" in message:
            print("Order queue shown.")
        data = s.recv(1024)
        decoded = data.decode()
        print(decoded)
        await asyncio.sleep(1)

    async def initialization(nr):  # Execute more tasks
        task1 = asyncio.create_task(connection())
        await task1
        task2 = asyncio.create_task(message_generator(nr,orders["settime"].format(nr, year, month, day, hour, minute, second) + NEW_LINE))
        await task2
        task3 = asyncio.create_task(message_generator(nr, orders["statusdevice"].format(nr) + NEW_LINE))
        await task3

    async def fetch_tray(nr): # Load specific tray you send to PLC
        task1 = asyncio.create_task(message_generator(nr, orders["fetchspecifictray"].format(nr, transID, tray, box_position, count, format_artnr, format_textarg) + NEW_LINE))
        await task1
        task2 = asyncio.create_task(queue_and_info_message(nr))
        await task2

    async def next_tray(): # Put your tray into queue
        pass

    async def open_invent():
        pass

    async def write_row():
        pass

    async def queue_and_info_message(nr):
        # loop = asyncio.get_running_loop()
        # while True:
            try:
                task1 = asyncio.create_task(message_generator(nr, orders["statusqueueall"].format(nr) + NEW_LINE))
                await task1
                task2 = asyncio.create_task(message_generator(nr, orders["statusinfoall"].format(nr) + NEW_LINE))
                await task2
            except KeyboardInterrupt:
                pass
    # Init function for calling async functions declared above
    async def init(nr):
        print(f"Init function started at {time.strftime('%X')}")
        await initialization(nr)
        print(f"Init function completed at {time.strftime('%X')}")

    asyncio.run(init(nr))
    asyncio.run(queue_and_info_message(nr))
    asyncio.run(fetch_tray(nr))