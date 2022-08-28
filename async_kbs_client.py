import socket
# import crc
import asyncio

"""
#! This script was written to control KBS lights.
#! NOT WORKING!!!
"""
# Constants definition
START = chr(int(b"02", 16)).encode('latin')
END = chr(int(b"03", 16)).encode('latin')
TRANS_END = chr(int(b"04", 16)).encode('latin')
CONTROLLER_NAME = "97xs"
LIGHT_NAME = "AnXw"
IP = "192.168.1.110"  # Controller IP
PORT = 10001  # Port to communicate


serverAddressPort = ((IP, PORT))
bufferSize = 1024
hostname = socket.gethostname()
localIP = socket.gethostbyname(hostname)

def message_generator():
    pass

def turn_on_light():
    pass

def show_number():
    pass

def status():
    pass

def light_blink():
    pass

def crc_computation(bytesdata):
    data = bytesdata
    # crc_calc = crc.CrcCalculator(crc.Crc16.CCITT)
    # checksum = crc_calc.calculate_checksum(data)
    # result = hex(checksum)[2:]
    # first = result[2:]
    # second = result[:2]
    # first_int = chr(int(first, 16))
    # second_int = chr(int(second, 16))
    # return first_int, second_int

# test = crc_computation(b'????0D?0000zzzz')
test2 = crc_computation(b'97xs0DR1')

# h = crc_computation(b'Hello')

# print(h[0].encode('latin') + h[1].encode('latin'))

# mainMessage = START + b"????0D?0000zzzz" + TRANS_END + test[0].encode('latin') + test[1].encode('latin') + END
mainMessage = START + b"97xs0DR1" + TRANS_END + test2[0].encode('latin') + test2[1].encode('latin') + END
print(mainMessage)
bytesToSend = mainMessage

# Create a UDP socket at client side

UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

UDPClientSocket.bind((localIP, PORT))

# Send to server using created UDP socket

UDPClientSocket.sendto(bytesToSend, serverAddressPort)

msgFromServer = UDPClientSocket.recvfrom(bufferSize)

msg = "Message from Controller {}".format(msgFromServer[0])

print(msg)
