import socket
import time
import asyncio

# Connection config constants
HOST = "127.0.0.1"
PORT = 20001
NEW_LINE = "\r\n"  # \r\n = Carriage return + Line feed
NR = 1
ACK = -1
OPENING = 1

# Defined actual date time
year = time.strftime("%Y")
month = time.strftime("%m")
day = time.strftime("%d")
hour = time.strftime("%H")
minute = time.strftime("%M")
second = time.strftime("%S")

# Dictionary with messages you can send
orders = {
    "status": "Status(MessId {}, AckMessId {}, Info All/Teach/Device, Tray , OrderQueue {}, ExtAck {})",  # Tray nr or All, OrderQueue nr or All
    "statusdevice": "Status(MessId {}, Info Device)",  # Derived from status above
    "statusqueueall": "Status(MessId {}, OrderQueue All)",  # Queue All
    "statusinfoall": "Status(MessId {}, AckMessId {}, Info All)",  # Info all
    "fetchtray": "FetchTray(MessId {}, TransID {}, Opening {}, Start 0/1, Type Out/In/OutNoReturn/InNoReturn, Tray {}, Box 'Position', ArtNr 'Number', ArtText 'Text')",
    "fetchspecifictray": "FetchTray(MessId {}, TransId {}, Opening {}, Start 1, Type OutNoReturn, Tray {}, Box {}, Count {}, ArtNr {}, ArtText {} )",  # Derived from fetchtray above
    "fetchpriotray": "FetchPrioTray(MessId {}, TransID {}, Opening {}, Start 0/1, Type Out/In/OutNoReturn/InNoReturn, Tray {}, Box 'Position', ArtNr 'Number', ArtText 'Text')",
    "nexttray": "NextTray(MessId {}, Opening {}, Tray1 {}, Tray2 {}, Tray3 {})",
    "openinvent": "OpenInvent(MessId {}, Opening {}, TransId {}, Enable 0)",
    "eraseorderqueue": "EraseOrderQueue(MessId {}, Opening {})",  # Opening default 1, or Opening All
    "writerow": "WriteRow(MessId {}, Opening {}, Row {}, Text {})",
    "lightbar": "LightBar(MessId {}, Opening {}, Type {}, XPos {}, XSize {}, YDigit {})",
    "laserpointer": "LaserPointer(MessId {}, LpId {}, Type {}, XPos {}, YPos {})",
    "sidetable": "SideTable(MessId {}, Opening {}, Type 'Out/In', XPos {})",
    "settime": "SetTime(MessId {}, Year {}, Month {}, Day {}, Hour {}, Minute {}, Second {})",  # Set actual date and time
    "ton": "Ton",  # Turn on connection timeout
    "toff": "Toff",  # Turn off connection timeout
}
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
artnr = "Test artiklu"
textarg = "Toto je popis k artiklu."
format_artnr = "< {}>".format(len(artnr)) + artnr
format_textarg = "< {}>".format(len(textarg)) + textarg
box_position = 1
tray = 4
count = 40
transID = 111


async def connection():
    try:
        print("Connecting...")
        await asyncio.sleep(1.5)
        s.connect((HOST, PORT))
        print("Connected successfully, communication begins..")
        await asyncio.sleep(1)
    except:
        print("Connection error.")


async def message_generator(message):
    global NR, ACK
    ACK += 1
    NR += 1
    if "SetTime" in message:
        print("Date time set.")
    elif "OrderQueue All" in message:
        print("Order queue shown.")
    s.send(message.encode())
    data = s.recv(1024)
    decoded = data.decode()
    print(decoded)
    await asyncio.sleep(1)


async def initialization():  # Execute more tasks
    task_connection = asyncio.create_task(connection())
    await task_connection
    task_settime = asyncio.create_task(
        message_generator(
            orders["settime"].format(
                NR, year, month, day, hour, minute, second
            ) + NEW_LINE
        )
    )
    await task_settime
    task_statusdevice = asyncio.create_task(
        message_generator(
            orders["statusdevice"].format(
                NR
            ) + NEW_LINE
        )
    )
    await task_statusdevice


async def fetch_tray():  # Load specific tray you send to PLC
    task_specifictray = asyncio.create_task(
        message_generator(
            orders["fetchspecifictray"].format(
                NR,
                transID,
                OPENING,
                tray,
                box_position,
                count,
                format_artnr,
                format_textarg,
            ) + NEW_LINE
        )
    )
    await task_specifictray
    task_queue_and_info_message = asyncio.create_task(queue_and_info_message())
    await task_queue_and_info_message


async def next_tray():  # Put your tray into queue
    pass


async def open_invent():
    task_openinvent = asyncio.create_task(
        message_generator(
            orders["openinvent"].format(
                NR,
                OPENING,
                transID
            ) + NEW_LINE
        )
    )
    await task_openinvent
    task_queue_and_info_message = asyncio.create_task(queue_and_info_message())
    await task_queue_and_info_message


async def write_row():
    pass


async def queue_and_info_message():
    # loop = asyncio.get_running_loop()
    # while True:
    try:
        task_status_queue_all = asyncio.create_task(
            message_generator(
                orders["statusqueueall"].format(
                    NR
                ) + NEW_LINE
            )
        )
        await task_status_queue_all
        task_status_info_all = asyncio.create_task(
            message_generator(
                orders["statusinfoall"].format(
                    NR,
                    ACK
                ) + NEW_LINE
            )
        )
        await task_status_info_all
    except KeyboardInterrupt:
        pass


# Init function for calling async functions declared above
async def init():
    print(f"Init function started at {time.strftime('%X')}")
    await initialization()
    print(f"Init function completed at {time.strftime('%X')}")


asyncio.run(init())
# asyncio.run(queue_and_info_message())
data = None
# asyncio.run(queue_and_info_message())
