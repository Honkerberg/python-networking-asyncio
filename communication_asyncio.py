import asyncio
import time
import random
import socket

from dataclasses import dataclass


# HOST = "127.0.0.1"
# PORT = 20001
NEW_LINE = "\r\n"
NR = 1
ACK = -1
OPENING = 1
ROW_1 = 1
ROW_2 = 2
# INVENTDONE = False
# RIDEFIN = False
# FETCH = False



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


@dataclass
class HWS:
    host: str = "127.0.0.1"
    port: int = 20001
    inventdone: bool = False
    ridefin: bool = False
    fetch: bool = False
    transid: int = 100

    async def connection(self):
        while s.connect_ex((self.host, self.port)) != 0:
            print(f"Trying to connect... ")
            await asyncio.sleep(0.5)
        else:
            print(f"Connected successfully, communication begins... ")


    # Sending and receiving function
    async def send_and_receive(self, command):
        global NR, ACK, transID, tray1, tray2, tray3, INVENTDONE, RIDEFIN, FETCH
        NR += 1
        ACK += 1
        s.send(command.encode())
        data = s.recv(10000)
        decoded = data.decode()
        print(decoded)
        print(f"fetch:{self.fetch}")
        print(f"ridefin:{self.ridefin}")
        print(f"inventdone:{self.inventdone}")
        print(ACK)
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
        if (b"PosCarrUp 0") in data and self.inventdone:
            # print("FINISHED\n")
            print(f"FINISHED")
            self.ridefin = True
            self.fetch = False
            self.inventdone = False
        elif b"IdInOpn_1" in data:
            if self.fetch:
                # print("TRAY AT OPENING\n") 
                print(f"TRAY AT OPENING")
        if b"TransDone" in data:  # PROBLEM SOLVED!
            data = None
            await hws.queue_and_info()
            if self.fetch:
                run_once = 0
                if run_once == 0:
                    task_extack = asyncio.create_task(hws.ext_ack())
                    task_open_invent = asyncio.create_task(hws.open_invent())
                    await task_extack
                    await task_open_invent
                    await hws.write_row(ROW_1)
                    await hws.write_row(ROW_2)  
                run_once = 1
            else:
                pass


    async def queue_and_info(self):
        await hws.status_info_all()


    # Erasing trays from queue
    async def erase_order_queue():
        command = "EraseOrderQueue(MessId {}, Opening All)" + NEW_LINE
        await hws.send_and_receive(command)


    async def write_row(rownum):
        command = (
            "WriteRow(MessId {}, Opening {}, Row {}, Text {})".format(
                NR, OPENING, rownum, "<  0>"
            )
            + NEW_LINE
        )
        await hws.send_and_receive(command)
        print(f"Row {rownum} written.")


    async def open_invent(self):
        self.inventdone = True
        command = (
            "OpenInvent(MessId {}, Opening {}, TransId {}, Enable 0)".format(
                NR, OPENING, self.transid
            )
            + "\r"
        )
        await hws.send_and_receive(command)


    async def ext_ack(self):
        command = f"Status(ExtAck{self.transid})\r"
        await hws.send_and_receive(command)
        print(f"Tray sending back.")


    async def status_info_all(self):
        if ACK == -1:
            command = f"Status(MessId {NR}, Info All){NEW_LINE}"
        else:
            command = f"Status(MessId {NR}, AckMessId {ACK}, Info All){NEW_LINE}"
        while True:
            await hws.send_and_receive(command)


    # Load specific tray to PLC
    async def fetch_tray(self, box_position, tray, count):
        self.fetch = True
        command = (
            "FetchTray(MessId {}, TransId {}, Opening {}, Start 1, Type OutNoReturn, Tray {}, Box {}, Count {}, ArtNr {}, ArtText {})".format(
                NR,
                self.transid,
                OPENING,
                tray,
                box_position,
                count,
                format_artnr,
                format_textarg,
            )
            + NEW_LINE
        )
        await hws.send_and_receive(command)
        print(f"TransID: {self.transid}, Tray: {tray}, Count: {count}, Box position: {box_position}")


    # Main function
    async def main(self):
        task_conn = asyncio.create_task(self.connection())
        task_status = asyncio.create_task(self.queue_and_info())
        # task_erase_order_queue = asyncio.create_task(erase_order_queue())

        # tasks = [task_conn, task_status, task_erase_order_queue, task_counter]
        tasks = [task_conn, task_status]

        task_fetch_tray = asyncio.create_task(hws.fetch_tray(box_position=10, tray=10, count=20))
        tasks.append(task_fetch_tray)
        await asyncio.gather(*tasks)

try:
    hws = HWS()
    asyncio.run(hws.main())
except KeyboardInterrupt:
    print('Stopped by keyboard.')