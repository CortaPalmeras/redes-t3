import socket
import sys
import struct
import typing

BUFFSIZE = 65536
HEADER_LEN = 5 * 4

class Header(typing.NamedTuple):
    dst_ip: int
    dst_port: int
    len: int
    id: int
    ttl: int

def pack_Header(header: Header) -> bytes:
    return struct.pack(f"5I", *header)

def unpack_header(header: bytes) -> Header:
    return Header(*struct.unpack("5I", header))

def ip_to_int(ip: str) -> int:
    return int.from_bytes(socket.inet_aton(ip))


if len(sys.argv) < 3:
    print(f"USO: python {sys.argv[0]} mi_ip:mi_puerto ip:puerto:mtu ...")
    exit(1)

my_addr = sys.argv[1].split(':', maxsplit=1)
my_addr = (ip_to_int(my_addr[0]), int(my_addr[1]))

links: dict[tuple[int, int], int] = dict()

for link in sys.argv[2:]:
    parts = link.split(':', maxsplit=2)
    ip = ip_to_int(parts[0])
    port = int(parts[1])
    mtu = int(parts[2])

    links[(ip,port)] = mtu

soc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
soc.bind(my_addr)

try:
    while True:
        msg = soc.recv(BUFFSIZE)

        data = msg[HEADER_LEN:]
        header = unpack_header(msg[:HEADER_LEN])
        dst_addr = (header.dst_ip, header.dst_port)

        if dst_addr == my_addr:
            print(data.decode())
        
        elif dst_addr in links.keys():
            if links[dst_addr] <= len(msg):
                pass # enviar
            else:
                pass # subdividir

        else:
            for addr, mtu in links.items():
                pass



except KeyboardInterrupt:
    print("\r")

soc.close()
