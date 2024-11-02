import struct
import time


class Header:
    def __init__(self, \
                 dst_ip: int, \
                 dst_port: int, \
                 size: int, \
                 id: int, \
                 offset: int, \
                 ttl: int) -> None:

        self.dst_ip = dst_ip
        self.dst_port = dst_port
        self.size = size
        self.id = id
        self.offset = offset
        self.ttl = ttl

HEADER_FIELDS = 6
HEADER_LEN = 4 * HEADER_FIELDS

def pack_header(header: Header) -> bytes:
    return struct.pack(f"{HEADER_FIELDS}I", header.dst_ip, header.dst_port, 
                                            header.size, header.id, 
                                            header.offset, header.ttl)

def unpack_header(header: bytes) -> Header:
    return Header(*struct.unpack(f"{HEADER_FIELDS}I", header))


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


