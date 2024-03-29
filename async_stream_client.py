import socket
import time
import asyncio
import random
import logging
import logging.handlers


# Connection config constants
HOST = "127.0.0.1"
# HOST = "192.168.1.15"
PORT = 20001
NEW_LINE = "\r\n"  # \r\n = Carriage return + Line feed
NR = 1
ACK = -1
OPENING = 1
ROW_1 = 1
ROW_2 = 2
INVENTDONE = False
RIDEFIN = False
FETCH = False


# Logging configuration
logger = logging.getLogger('lift_communication')
logger.setLevel(logging.INFO)

fh = logging.handlers.RotatingFileHandler('lift.log', backupCount=10, maxBytes=4000000)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

formatter = logging.Formatter(fmt='%(asctime)s :: %(name)s :: %(levelname)-8s :: %(message)s')

fh.setFormatter(formatter)
ch.setFormatter(formatter)

logger.addHandler(fh)
logger.addHandler(ch)

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
    "fetchpriotray": "FetchPrioTray(MessId {}, TransID {}, Opening {}, Start 1, Type Out/In/OutNoReturn/InNoReturn, Tray {}, Box 'Position', ArtNr 'Number', ArtText 'Text')",
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
tray1 = 0
tray2 = 0
tray3 = 0


# Connect function
async def connection():
    while s.connect_ex((HOST, PORT)) != 0:
        logger.info(f"Trying to connect... ")
        await asyncio.sleep(0.5)
    else:
        logger.info(f"Connected successfully, communication begins... ")


# Sending and receiving function
async def send_and_receive(command):
    global NR, ACK, transID, tray1, tray2, tray3, INVENTDONE, RIDEFIN, FETCH
    NR += 1
    ACK += 1
    s.send(command.encode())
    data = s.recv(10000)
    decoded = data.decode()
    print(decoded)
    await asyncio.sleep(0.5)
    if "EraseOrderQueue" in command:
        # print("QUEUE ERASED\n")
        logger.info(f"QUEUE ERASED")
    elif "FetchTray" in command:
        # print("NEW TRAY FETCHED\n")
        logger.info(f"NEW TRAY FETCHED")
    if b"IdOnUpLevel" in data:
        # print("TRAY RIDE\n")
        logger.info(f"TRAY RIDE")
    if (b"PosCarrUp 0") in data and INVENTDONE:
        # print("FINISHED\n")
        logger.info(f"FINISHED")
        RIDEFIN = True
    elif b"IdInOpn_1" in data:
        if FETCH:
            # print("TRAY AT OPENING\n") 
            logger.info(f"TRAY AT OPENING")
    # if b"TransDone" in data:  # PROBLEM SOLVED!
    #     data = None
    #     await queue_and_info()
    #     if FETCH:
    #         run_once = 0
    #         if run_once == 0:
    #             task_extack_and_open_invent = asyncio.create_task(extack_and_open_invent())
    #             await task_extack_and_open_invent
    #             await write_row(ROW_1)
    #             await write_row(ROW_2)  
    #         run_once = 1
        else:
            pass


# Connect and status device tasks
async def status_device():
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
    global FETCH
    FETCH = True
    box_position = random.randint(1, 10)
    tray = random.randint(1, 50)
    count = random.randint(1, 60)
    await asyncio.sleep(random.uniform(5.0, 6.0))
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
    logger.info(f"TransID: {transID}, Tray: {tray}, Count: {count}, Box position: {box_position}")


# Shows next trays if fetched - not used for now, used when fetched more trays
async def next_tray():
    command = "NextTray(MessId {}, Opening {}, Tray1 {}, Tray2 {}, Tray3 {})".format(NR, OPENING, tray1, tray2, tray3) + NEW_LINE
    await send_and_receive(command)
    if tray1 == 0 and tray2 == 0 and tray3 == 0:
        logger.info(f"Next tray is none.")
    else:
        logger.info(f"Tray1: {tray1}, Tray2: {tray2}, Tray3: {tray3}")

# Open inventory and put tray back
async def extack_and_open_invent():
    global INVENTDONE
    INVENTDONE = True
    command = (
        "OpenInvent(MessId {}, Opening {}, TransId {}, Enable 0)".format(
            NR, OPENING, transID
        )
        + "\r"
    )
    await send_and_receive(command)
    logger.info(f"Tray sending back.")


# Write row to article text
async def write_row(rownum):
    command = (
        "WriteRow(MessId {}, Opening {}, Row {}, Text {})".format(
            NR, OPENING, rownum, "<  0>"
        )
        + NEW_LINE
    )
    await send_and_receive(command)
    logger.info(f"Row {rownum} written.")


# Shows info about all trays
async def trayall():
    command = "Status(MessId {}, Tray All)".format(NR) + NEW_LINE
    await send_and_receive(command)


# Notify what task is done
async def task_done(taskname):
    logger.info(f"{taskname.get_name()} Done. Waiting... ")


# Main function for calling async functions declared above
async def main():
    global INVENTDONE, RIDEFIN, FETCH
    FETCH = False
    INVENTDONE = False
    RIDEFIN = False
    await status_device()
    # await erase_order_queue()
    # task_fetchtray = asyncio.create_task(fetch_tray())
    # task_fetchtray.set_name("FetchTrayTask")
    # while not task_fetchtray.done():
    #     await asyncio.sleep(0.5)
    #     await queue_and_info()
    #     if task_fetchtray.done():
    #         await asyncio.wait_for(task_fetchtray, 0.5)
    #         await task_done(task_fetchtray)
    #         logger.info(f"TRAY LOADING..")
    #         await asyncio.sleep(3)                                                                                                                                                                                                                          
    #         await queue_and_info()
    while True:
        task_idle = asyncio.create_task(queue_and_info())
        await task_idle
        if RIDEFIN:
            break

try:
    logger.info(f"Main function started at {time.strftime('%X')}")
    asyncio.run(connection())
    continue_ride = "y"
    while continue_ride == "y" or continue_ride == "Y":
        transID = random.randint(100, 110)
        asyncio.run(main())
        continue_ride = input("Do you want another ride? Y/N\n")
        if continue_ride == "n" or continue_ride == "N":
            logger.info("SEE YOU SOON!")
            break
except KeyboardInterrupt:
    logger.warning(f"Keyboard interrupt.")
except ConnectionError:
    logger.error(f"Connection error, shutdown.")
finally:
    logger.info(f"Main function completed at {time.strftime('%X')}")
