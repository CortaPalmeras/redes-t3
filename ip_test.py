import time
import ip

print("FragmentedMessage tests:")

print("ideal case: ", end='')
msg = ip.FragmentedMessage(10)
msg.add(b'01', 0)
msg.add(b'23', 2)
msg.add(b'45', 4)
msg.add(b'67', 6)
msg.add(b'89', 8)
assert msg.is_complete() == True
assert msg.reconstruct() == b'0123456789'
print("passed")

print("empty: ", end='')
msg = ip.FragmentedMessage(0)
assert msg.is_complete() == True
assert msg.reconstruct() == b''
msg.add(b'', 0)
assert msg.is_complete() == True
assert msg.reconstruct() == b''
msg.add(b'', 5)
assert msg.is_complete() == True
assert msg.reconstruct() == b''

msg = ip.FragmentedMessage(0)
msg.add(b'0', 0)
assert msg.is_complete() == True
assert msg.reconstruct() == b''
msg.add(b'0', 5)
assert msg.is_complete() == True
assert msg.reconstruct() == b''
print("passed")

print("no fragmentation: ", end='')
msg = ip.FragmentedMessage(10)
msg.add(b'0123456789', 0)
assert msg.is_complete() == True
assert msg.reconstruct() == b'0123456789'


print("out of order: ", end='')
msg = ip.FragmentedMessage(10)
msg.add(b'23', 2)
msg.add(b'89', 8)
msg.add(b'45', 4)
msg.add(b'01', 0)
msg.add(b'67', 6)
assert msg.is_complete() == True
assert msg.reconstruct() == b'0123456789'
print("passed")

print("extra stuff: ", end='')
msg = ip.FragmentedMessage(10)
msg.add(b'23', 2)
msg.add(b'--', 2)
msg.add(b'89', 8)
msg.add(b'--', 8)
msg.add(b'01', 0)
msg.add(b'--', 0)
msg.add(b'--', 1)
msg.add(b'--', 2)
msg.add(b'--', 3)
msg.add(b'45', 4)
msg.add(b'--', 4)
msg.add(b'--', 5)
msg.add(b'67', 6)
msg.add(b'--', 6)
msg.add(b'--', 7)
msg.add(b'--', 8)
msg.add(b'--', 9)
assert msg.is_complete() == True
assert msg.reconstruct() == b'0123456789'
print("passed")


print("out of bounds: ", end='')
msg = ip.FragmentedMessage(10)
msg.add(b'-' * 10, 1)
msg.add(b'--', 9)
msg.add(b'01', 0)
msg.add(b'23', 2)
msg.add(b'-' * 7, 4)
msg.add(b'45', 4)
msg.add(b'67', 6)
msg.add(b'-' * 9, 3)
msg.add(b'---', 8)
msg.add(b'89', 8)
assert msg.is_complete() == True
assert msg.reconstruct() == b'0123456789'
print("passed")

print("Defragmenter tests:")

print("ideal case: ")
print("expected: 0123456789")
print("got     : ", end='')
df = ip.Defragmenter()
hdr = ip.Header(dst_ip=0, dst_port=0, size=10, id=0, offset=0, ttl=100)
df.add_segment(hdr, b'0123456789')

print("expected: 01234567890123456789")
print("got     : ", end='')
hdr = ip.Header(dst_ip=0, dst_port=0, size=20, id=1, offset=0, ttl=100)
df.add_segment(hdr, b'0123456789')
hdr = ip.Header(dst_ip=0, dst_port=0, size=20, id=1, offset=10, ttl=100)
df.add_segment(hdr, b'0123456789')


print("empty case: ")
print("expected: ")
print("got     : ", end='')
df = ip.Defragmenter()
hdr = ip.Header(dst_ip=0, dst_port=0, size=0, id=0, offset=0, ttl=100)
df.add_segment(hdr, b'')

print("expected: ")
print("got     : ", end='')
hdr = ip.Header(dst_ip=0, dst_port=0, size=0, id=1, offset=0, ttl=100)
df.add_segment(hdr, b'0123456789')

print("out of order: ")
print("expected: 0123456789")
print("got     : ", end='')
hdr = ip.Header(dst_ip=0, dst_port=0, size=10, id=1, offset=2, ttl=100)
df.add_segment(hdr, b'23')
hdr = ip.Header(dst_ip=0, dst_port=0, size=10, id=1, offset=6, ttl=100)
df.add_segment(hdr, b'67')
hdr = ip.Header(dst_ip=0, dst_port=0, size=10, id=1, offset=0, ttl=100)
df.add_segment(hdr, b'01')
hdr = ip.Header(dst_ip=0, dst_port=0, size=10, id=1, offset=8, ttl=100)
df.add_segment(hdr, b'89')
hdr = ip.Header(dst_ip=0, dst_port=0, size=10, id=1, offset=4, ttl=100)
df.add_segment(hdr, b'45')

print("timeout: ")
print("expected: 0123456789")
print("got     : ", end='')
hdr = ip.Header(dst_ip=0, dst_port=0, size=10, id=1, offset=0, ttl=100)
df.add_segment(hdr, b'-' * 4)
hdr = ip.Header(dst_ip=0, dst_port=0, size=10, id=1, offset=4, ttl=100)
df.add_segment(hdr, b'-' * 4)
time.sleep(ip.MSG_TIMEOUT)
hdr = ip.Header(dst_ip=0, dst_port=0, size=10, id=1, offset=2, ttl=100)
df.add_segment(hdr, b'23')
hdr = ip.Header(dst_ip=0, dst_port=0, size=10, id=1, offset=6, ttl=100)
df.add_segment(hdr, b'67')
hdr = ip.Header(dst_ip=0, dst_port=0, size=10, id=1, offset=0, ttl=100)
df.add_segment(hdr, b'01')
hdr = ip.Header(dst_ip=0, dst_port=0, size=10, id=1, offset=8, ttl=100)
df.add_segment(hdr, b'89')
hdr = ip.Header(dst_ip=0, dst_port=0, size=10, id=1, offset=4, ttl=100)
df.add_segment(hdr, b'45')


