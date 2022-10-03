import asyncio
import time
import random
import socket


HOST = "127.0.0.1"
PORT = 20001
NEW_LINE = "\r\n"
NR = 1
ACK = -1
OPENING = 1
ROW_1 = 1
ROW_2 = 2
INVENTDONE = False
RIDEFIN = False
FETCH = False
CNTR = 0

transID = random.randint(100, 110)


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


async def connection():
    while s.connect_ex((HOST, PORT)) != 0:
        print(f"Trying to connect... ")
        await asyncio.sleep(0.5)
    else:
        print(f"Connected successfully, communication begins... ")


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
        print(f"QUEUE ERASED")
    elif "FetchTray" in command:
        # print("NEW TRAY FETCHED\n")
        print(f"NEW TRAY FETCHED")
    if b"IdOnUpLevel" in data:
        # print("TRAY RIDE\n")
        print(f"TRAY RIDE")
    if (b"PosCarrUp 0") in data and INVENTDONE:
        # print("FINISHED\n")
        print(f"FINISHED")
        RIDEFIN = True
    elif b"IdInOpn_1" in data:
        if FETCH:
            # print("TRAY AT OPENING\n") 
            print(f"TRAY AT OPENING")
    if b"TransDone" in data:  # PROBLEM SOLVED!
        data = None
        await queue_and_info()
        if FETCH:
            run_once = 0
            if run_once == 0:
                task_extack_and_open_invent = asyncio.create_task(extack_and_open_invent())
                await task_extack_and_open_invent
                await write_row(ROW_1)
                await write_row(ROW_2)  
            run_once = 1
        else:
            pass


async def queue_and_info():
    await status_info_all()


# Erasing trays from queue
async def erase_order_queue():
    command = "EraseOrderQueue(MessId {}, Opening All)" + NEW_LINE
    await send_and_receive(command)


async def write_row(rownum):
    command = (
        "WriteRow(MessId {}, Opening {}, Row {}, Text {})".format(
            NR, OPENING, rownum, "<  0>"
        )
        + NEW_LINE
    )
    await send_and_receive(command)
    print(f"Row {rownum} written.")


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
    print(f"Tray sending back.")


async def status_info_all():
    if ACK == -1:
        command = f"Status(MessId {NR}, Info All){NEW_LINE}"
    else:
        command = f"Status(MessId {NR}, AckMessId {ACK}, Info All){NEW_LINE}"
    while True:
        await send_and_receive(command)


async def counter():
    n = 0
    while True:
        print(n)
        n+=1
        await asyncio.sleep(1)

# Load specific tray to PLC
async def fetch_tray():
    global FETCH
    FETCH = True
    box_position = random.randint(1, 10)
    tray = random.randint(1, 50)
    count = random.randint(1, 60)

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
    print(f"TransID: {transID}, Tray: {tray}, Count: {count}, Box position: {box_position}")


# Main function
async def main():
    task_counter = asyncio.create_task(counter())
    task_conn = asyncio.create_task(connection())
    task_status = asyncio.create_task(queue_and_info())
    task_erase_order_queue = asyncio.create_task(erase_order_queue())

    tasks = [task_conn, task_status, task_erase_order_queue, task_counter]

    # task_fetch_tray = asyncio.create_task(fetch_tray())
    # tasks.append(task_fetch_tray)

    await asyncio.gather(*tasks)

try:
    asyncio.run(main())
except KeyboardInterrupt:
    print('Stopped by keyboard.')