import os
import random
import socket
import threading
import struct
import time
import queue
import sys
import io

class Header:
    def __init__(self, \
                 dst_ip: int, \
                 dst_port: int, \
                 size: int, \
                 id: int, \
                 offset: int, \
                 ttl: int) -> None:

        self.dst_ip: int = dst_ip
        self.dst_port: int = dst_port
        self.size: int = size
        self.id: int = id
        self.offset: int = offset
        self.ttl: int = ttl

HEADER_FIELDS = 6
HEADER_LEN = 4 * HEADER_FIELDS

def pack_header(header: Header) -> bytes:
    return struct.pack(f"{HEADER_FIELDS}I", header.dst_ip, header.dst_port, 
                                            header.size, header.id, 
                                            header.offset, header.ttl)

def unpack_header(header: bytes) -> Header:
    dst_ip: int
    dst_port: int
    size: int
    id: int
    offset: int
    ttl: int
    dst_ip, dst_port, size, id, offset, ttl = struct.unpack(f"{HEADER_FIELDS}I", header)
    return Header(dst_ip, dst_port, size, id, offset, ttl)


MSG_TIMEOUT = 1

class FragmentedMessage:
    def __init__(self, len: int) -> None:
        self.len: int = len
        self.next: int = 0
        self.msg: dict[int, bytes] = dict()
        self.offsets: set[int] = set()

    def is_complete(self) -> bool:
        return self.len == self.next

    def add(self, msg: bytes, offset: int) -> None:
        if offset < self.next \
            or offset + len(msg) > self.len \
            or len(msg) <= 0 \
            or offset in self.offsets:
            return

        self.msg[offset] = msg
        self.offsets.add(offset)

        while self.next in self.offsets:
            self.next += len(self.msg[self.next])

    def reconstruct(self) -> bytes:
        ret = b''
        while len(ret) < self.next:
            ret += self.msg[len(ret)]
        return ret
        

class Defragmenter:
    def __init__(self) -> None:
        self.messages: dict[int, FragmentedMessage] = dict()
        self.timeouts: dict[int, float] = dict()

    def check_timeouts(self) -> None:
        current_time = time.time()
        timedout_keys = [key for key, timeout in self.timeouts.items() \
                            if current_time - timeout > MSG_TIMEOUT]

        for key in timedout_keys:
            del self.timeouts[key]
            del self.messages[key]

    def add_segment(self, header: Header, data: bytes) -> bytes | None:
        self.check_timeouts()

        if header.id not in self.messages.keys():
            self.messages[header.id] = FragmentedMessage(header.size)
            self.timeouts[header.id] = time.time()
        
        msg = self.messages[header.id]
        msg.add(data, header.offset)
        self.timeouts[header.id] = time.time()

        if msg.is_complete():
            ret = msg.reconstruct()
            del self.messages[header.id]
            del self.timeouts[header.id]
            return ret


BUFFSIZE = 2 ** 15

def ip_to_int(ip: str) -> int:
    return int.from_bytes(socket.inet_aton(socket.gethostbyname(ip)))

def int_to_ip(ip: int) -> str:
    return socket.inet_ntoa(ip.to_bytes(4))

flag = "--enviar"
help_string = f"""\
USOS: {sys.orig_argv[0]} {sys.argv[0]} mi_ip:mi_puerto ip:puerto:mtu ...
      {sys.orig_argv[0]} {sys.argv[0]} {flag} archivo ip_partida:puerto_partida ip_destino:puerto_destino ttl"""

if len(sys.argv) < 2:
    print(help_string, file=sys.stderr)
    exit(1)

if sys.argv[1] == flag:
    if len(sys.argv) < 6:
        print(help_string, file=sys.stderr)
        exit(1)

    mal_argumento = 2
    try:
        file = open(sys.argv[2], "rb")
        size = file.seek(0, io.SEEK_END)
        _ = file.seek(0, io.SEEK_SET)

        mal_argumento = 3
        src_addr = sys.argv[3].split(':', maxsplit=1)
        src_addr = (src_addr[0], int(src_addr[1]))

        mal_argumento = 4
        dst_addr = sys.argv[4].split(':', maxsplit=1)
        dst_ip, dst_port = (ip_to_int(dst_addr[0])), int(dst_addr[1])

        mal_argumento = 5
        ttl = int(sys.argv[5])

    except:
        print(f"Error en el argumento {sys.argv[mal_argumento]}", file=sys.stderr)
        exit(1)

    id = random.randrange(0, 2 ** 32)
    offset = 0

    header = Header(dst_ip=dst_ip, dst_port=dst_port, size=size, 
                    id=id, offset=offset, ttl=ttl)

    soc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    while file.tell() != size:
        data = file.read(BUFFSIZE - HEADER_LEN)
        _ = soc.sendto(pack_header(header) + data, src_addr)
        header.offset += len(data)

    exit(0)


try: 
    my_ip, my_port = sys.argv[1].split(':', maxsplit=1)
    my_addr = (socket.gethostbyname(my_ip), int(my_port))

except:
    print(f"Error en el argumento {sys.argv[1]}", file=sys.stderr)
    exit(1)

mtus: dict[tuple[str, int], int] = dict()

for link in sys.argv[2:]:
    try: 
        parts = link.split(':', maxsplit=2)
        ip = socket.gethostbyname(parts[0])
        port = int(parts[1])
        mtu = int(parts[2])

        if mtu <= HEADER_LEN:
            print(f"""Error en  el argumento {link}, todos los MTUs deben ser mayores 
al tamaño del header ({HEADER_LEN} bytes)""", file=sys.stderr)
            exit(1)

        mtus[(ip,port)] = mtu

    except:
        print(f"Error en el argumento {link}", file=sys.stderr)
        exit(1)

links: list[tuple[str,int]] = list(mtus.keys())
max_mtu = max(mtus.values()) if len(mtus) > 0 else 0


wait_before_send = 0
def sendto(soc: socket.socket, msg: bytes, addr: tuple[str, int]) -> None:
    global wait_before_send

    if wait_before_send >= 10:
        time.sleep(0.01)
        wait_before_send = 0

    wait_before_send += 1
    _ = soc.sendto(msg, addr)



reciever_soc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
reciever_soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
reciever_soc.bind(my_addr)

msg_queue: queue.Queue[bytes] = queue.Queue()

# un thread separado lee los mensajes recibidos para que no se atasque
# la cola del kernel y que este empiece a botarlos
def get_messages() -> None:
    while True:
        msg_queue.put(reciever_soc.recv(BUFFSIZE))

reciever_thread = threading.Thread(target=get_messages, daemon=True)
reciever_thread.start()

sender_soc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

try:
    segments = Defragmenter()

    while True:
        msg = msg_queue.get()

        if len(msg) <= HEADER_LEN:
            continue

        data = msg[HEADER_LEN:]
        header = unpack_header(msg[:HEADER_LEN])
        dst_addr = (int_to_ip(header.dst_ip), header.dst_port)

        header.ttl -= 1

        # si este es el destino del mensaje entonces se reconstruye y se imprime
        if dst_addr == my_addr:
            full_msg = segments.add_segment(header, data)
            if full_msg != None:
                _ = os.write(sys.stdout.fileno(), full_msg)

        # si termina el tiempo de vida del paquete este se bota
        elif header.ttl == 0 or max_mtu == 0:
            continue
        
        # el mensaje es enviado directamente a su destino si es que este se
        # encuentra en la lista de enlaces y el mensaje cabe completo
        elif dst_addr in links and len(msg) <= mtus[dst_addr]:
            _ = sendto(sender_soc, pack_header(header) + data, dst_addr)
            links.remove(dst_addr)
            links.append(dst_addr)

        # si existe agún enlace por el cual quepa el mensaje completo,
        # se busca por cual y se le evía, luego el enlace se mueve al
        # final de la lista de enlaces para que se vayan rotando
        elif len(msg) <= max_mtu:
            i = 0
            while mtus[links[i]] < len(msg):
                i += 1

            _ = sendto(sender_soc, pack_header(header) + data, links[i])
            links.append(links.pop(i))

        # si el mensaje no cabe en ningún enlace entonces se fragmenta y 
        # distribuye entre todos los enlaces
        else:
            sent_data = 0
            wait = 0

            while sent_data < len(data):
                next_addr = links.pop(0)
                fragment_size = mtus[next_addr] - HEADER_LEN
                fragment_data = data[sent_data : sent_data + fragment_size]

                _ = sendto(sender_soc, pack_header(header) + fragment_data, next_addr)
                links.append(next_addr)

                sent_data += fragment_size
                header.offset += fragment_size


except KeyboardInterrupt:
    sender_soc.close()
    reciever_soc.close()
    print("conección cerrada", file=sys.stderr)
    exit()


