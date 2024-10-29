import struct
import time

MSG_TIMEOUT = 1

class Header:
    def __init__(self, header: bytes) -> None:
        self.dst_ip: int
        self.dst_port: int
        self.len: int
        self.id: int
        self.offset: int
        self.ttl: int

        self.dst_ip, self.dst_port, self.len, self.id,\
        self.offset, self.ttl = struct.unpack("6I", header)

    def pack(self) -> bytes:
        return struct.pack(f"6I", (self.dst_ip, self.dst_port, 
                                   self.len, self.id, self.ttl))

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
            or len(msg) <= 0 \
            or offset + len(msg) > self.len:
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
        for key, timeout in self.timeouts.items():
            if current_time - timeout > MSG_TIMEOUT:
                del self.timeouts[key]
                del self.messages[key]

    def add_segment(self, header: Header, data: bytes) -> None:
        self.check_timeouts()

        if header.id not in self.messages.keys():
            self.messages[header.id] = FragmentedMessage(header.len)
            self.timeouts[header.id] = time.time()
        
        msg = self.messages[header.id]
        msg.add(data, header.offset)
        self.timeouts[header.id] = time.time()

        if msg.is_complete():
            print(msg.reconstruct().decode())
            del self.messages[header.id]
            del self.timeouts[header.id]

