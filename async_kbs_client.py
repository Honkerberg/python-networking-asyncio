import socket
import asyncio


start = "\x02"
end = "\x03"

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


async def conn():
    print("Connecting..")
    s.connect(("127.0.0.1", 4101))
    print("Connected")

async def msg():
    message = start + "00001050STZS01" + end + "\r\n"
    print(message)
    s.send(message.encode())
    data = s.recv(1000)
    decode = data.decode()
    print(decode)


async def main():
    await conn()
    await msg()


try:
    asyncio.run(main())
except KeyboardInterrupt:
    print("Stop.")