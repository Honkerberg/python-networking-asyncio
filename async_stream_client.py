import socket
import time
import asyncio
import random
# import sys


# Connection config constants
HOST = "127.0.0.1"
PORT = 20001
NEW_LINE = "\r\n"  # \r\n = Carriage return + Line feed
NR = 1
ACK = -1
OPENING = 1
ROW_1 = 1
ROW_2 = 2
INVENTORY = False

# Defined actual date time
year = time.strftime("%Y")
month = time.strftime("%m")
day = time.strftime("%d")
hour = time.strftime("%H")
minute = time.strftime("%M")
second = time.strftime("%S")

# Dictionary with messages - examples
orders = {
    "status": "Status(MessId {}, AckMessId {}, Info All/Teach/Device, Tray , OrderQueue {}, ExtAck {})",  # Tray nr or All, OrderQueue nr or All
    "statusextack": "Status(MessId {}, ExtAck {}, Info All)",  # External acknowledge
    "statusdevice": "Status(MessId {}, Info Device)",  # Derived from status above
    "statusqueueall": "Status(MessId {}, OrderQueue All)",  # Queue All
    "statusinfoall": "Status(MessId {}, AckMessId {}, Info All)",  # Info all
    "fetchtray": "FetchTray(MessId {}, TransID {}, Opening {}, Start 0/1, Type Out/In/OutNoReturn/InNoReturn, Tray {}, Box 'Position', ArtNr 'Number', ArtText 'Text')",
    "fetchspecifictray": "FetchTray(MessId {}, TransId {}, Opening {}, Start 1, Type OutNoReturn, Tray {}, Box {}, Count {}, ArtNr {}, ArtText {} )",  # Derived from fetchtray above
    "fetchpriotray": "FetchPrioTray(MessId {}, TransID {}, Opening {}, Start 0/1, Type Out/In/OutNoReturn/InNoReturn, Tray {}, Box 'Position', ArtNr 'Number', ArtText 'Text')",
    "nexttray": "NextTray(MessId {}, Opening {}, Tray1 {}, Tray2 {}, Tray3 {})",
    "openinvent": "OpenInvent(MessId {}, Opening {}, TransId {}, Enable 0)",
    "eraseorderqueue": "EraseOrderQueue(MessId {}, Opening All)",  # Opening default 1, or Opening All
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
textinfo = "Test zpravy WriteRow"
format_textinfo = "< {}>".format(len(textinfo)) + textinfo
box_position = random.randint(1, 10)
tray = random.randint(1, 50)
count = random.randint(1, 60)
transID = random.randint(100, 110)
tray1 = 0
tray2 = 0
tray3 = 0


# Connect function
async def connection():
    try:
        print("Connecting...")
        await asyncio.sleep(1)
        s.connect((HOST, PORT))
        print("Connected successfully, communication begins..")
        await asyncio.sleep(1)
    except:
        print("Connection error.")


# Sending and receiving function
async def send_and_receive(command):
    global NR, ACK, transID, tray1, tray2, tray3
    NR += 1
    ACK += 1
    s.send(command.encode())
    data = s.recv(10000)
    decoded = data.decode()
    print(decoded)
    if "EraseOrderQueue" in command:
        print("Queue erased.\n")
    elif "FetchTray" in command:
        print("New tray fetched.\n")
    if b"TransDone" in data:
        data = None
        await queue_and_info()
        run_once = 0
        if run_once == 0:
            await extack_and_open_invent()
            await write_row(ROW_1)
            await write_row(ROW_2)
            run_once = 1
    await asyncio.sleep(0.2)


# Connect and status device tasks
async def connect_and_status_device():
    await connection()
    command = (
        "SetTime(MessId {}, Year {}, Month {}, Day {}, Hour {}, Minute {}, Second {})".format(
            NR, year, month, day, hour, minute, second
        )
        + NEW_LINE
    )
    await send_and_receive(command)


# Function shows queue in PLC
async def status_queue_all():
    command = "Status(MessId {}, OrderQueue All)".format(NR) + NEW_LINE
    await send_and_receive(command)


# Function shows info about PLC machine and elevator position
async def status_info_all():
    if ACK == -1:
        command = "Status(MessId {}, Info All)".format(NR) + NEW_LINE
    else:
        command = "Status(MessId {}, AckMessId {}, Info All)".format(NR, ACK) + NEW_LINE
    await send_and_receive(command)


# Queue and elevator position
async def queue_and_info():
    await status_queue_all()
    await status_info_all()


# Erasing trays from queue
async def erase_order_queue():
    command = "EraseOrderQueue(MessId {}, Opening All)" + NEW_LINE
    await send_and_receive(command)


# Load specific tray to PLC
async def fetch_tray():
    await asyncio.sleep(random.uniform(1.0, 10.0))
    command = (
        "FetchTray(MessId {}, TransId {}, Opening {}, Start 1, Type OutNoReturn, Tray {}, Box {}, Count {}, ArtNr {}, ArtText {})".format(
            NR,
            transID,
            OPENING,
            tray,
            box_position,
            count,
            format_artnr,
            format_textarg,
        )
        + NEW_LINE
    )
    await send_and_receive(command)
    print(
        "TransID: {}, Tray: {}, Count: {}, Box position: {}\n".format(
            transID, tray, count, box_position
        )
    )


# Shows next trays if fetched - not used for now
async def next_tray():
    command = "NextTray(MessId {}, Opening {}, Tray1 {}, Tray2 {}, Tray3 {})".format(NR, OPENING, tray1, tray2, tray3) + NEW_LINE
    await send_and_receive(command)
    if tray1 == 0 and tray2 == 0 and tray3 == 0:
        print("Next tray is none.\n")
    else:
        print("Tray1: {}, Tray2: {}, Tray3: {}\n".format(tray1, tray2, tray3))

# Open inventory and put tray back
async def extack_and_open_invent():
    command = (
        "OpenInvent(MessId {}, Opening {}, TransId {}, Enable 0)".format(
            NR, OPENING, transID
        )
        + "\r"
    )
    await send_and_receive(command)
    print("Tray sending back..\n")


# Write row to article text
async def write_row(rownum):
    command = (
        "WriteRow(MessId {}, Opening {}, Row {}, Text {})".format(
            NR, OPENING, rownum, "<  0>"
        )
        + NEW_LINE
    )
    await send_and_receive(command)
    print("Row {} written.".format(rownum))


# Shows info about all trays
async def trayall():
    command = "Status(MessId {}, Tray All)".format(NR) + NEW_LINE
    await send_and_receive(command)


# Notify what task is done
async def task_done(taskname):
    print(taskname.get_name() + " Done. Waiting..\n")


# Main function for calling async functions declared above
async def main():
    await connect_and_status_device()
    await trayall()
    await erase_order_queue()
    task_fetchtray = asyncio.create_task(fetch_tray())
    task_fetchtray.set_name("FetchTrayTask")
    while not task_fetchtray.done():
        print("Waiting for new tray...\n")
        await queue_and_info()
        if task_fetchtray.done() == True:
            await task_done(task_fetchtray)
            await next_tray()
            await asyncio.sleep(1)
    while True:
        await queue_and_info()


try:
    # sys.stdout = open("log.txt", "w")
    print(f"Main function started at {time.strftime('%X')}")
    asyncio.run(main())
except KeyboardInterrupt:
    print("Keyboard interrupt.")
finally:
    print(f"Main function completed at {time.strftime('%X')}")
    # sys.stdout.close()
