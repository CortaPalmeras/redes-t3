import socket
import sys

from ip import Header

BUFFSIZE = 65536
HEADER_LEN = 5 * 4

def ip_to_int(ip: str) -> int:
    return int.from_bytes(socket.inet_aton(ip))

if len(sys.argv) < 3:
    print(f"USO: <python> {sys.argv[0]} mi_ip:mi_puerto ip:puerto:mtu ...")
    exit(1)

my_addr = sys.argv[1].split(':', maxsplit=1)
my_addr = (ip_to_int(my_addr[0]), int(my_addr[1]))

mtus: dict[tuple[int, int], int] = dict()
links: list[tuple[int,int]] = list()

for link in sys.argv[2:]:
    parts = link.split(':', maxsplit=2)
    ip = ip_to_int(parts[0])
    port = int(parts[1])
    mtu = int(parts[2])

    mtus[(ip,port)] = mtu

links = list(mtus.keys())

MAX_MTU = max(mtus.values())


soc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
soc.bind(my_addr)


try:
    while True:
        msg = soc.recv(BUFFSIZE)

        data = msg[HEADER_LEN:]
        header = Header(msg[:HEADER_LEN])
        dst_addr = (header.dst_ip, header.dst_port)

        header.ttl -= 1

        # si este es el destino del mensaje entonces se reconstruye
        # y se imprime
        if dst_addr == my_addr:
            print(data.decode())


        # si termina el tiempo de vida del paquete este se bota
        elif header.ttl == 0:
            continue
        

        # el mensaje es enviado directamente a su destino si 
        # este se encuentra en la lista de enlaces.
        elif dst_addr in links and mtus[dst_addr] <= len(msg):
            _ = soc.sendto(header.pack() + data, dst_addr)


        # si el mensaje cabe por algún enlace, se envía por ahí,
        # moviendo ese enlace al final de la lista
        elif len(msg) <= MAX_MTU:
            i = 0
            while mtus[links[i]] < len(msg):
                i += 1

            _ = soc.sendto(header.pack() + data, links[i])
            links.append(links.pop(i))


        # si el mensaje no cabe en ningún enlace entonces se 
        # fragmenta y distribuye
        else:
            for addr, mtu in mtus.items():
                pass 

except KeyboardInterrupt:
    print("\r")

finally:
    soc.close()

