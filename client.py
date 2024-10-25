import socket as skt

IP = "127.0.0.1"
PORT = 12321
BUFF_SIZE = 1080

soc = skt.socket(family = skt.AF_INET,
                 type = skt.SOCK_DGRAM)

msg = "Hola, Mundo!"
_ = soc.sendto(msg.encode(), (IP, PORT))
_ = soc.sendto(msg.encode(), (IP, PORT))

soc.close()

