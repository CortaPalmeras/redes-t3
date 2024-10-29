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
msg.add(b'89', 8)
msg.add(b'45', 4)
msg.add(b'67', 6)
msg.add(b'45', 4)
msg.add(b'01', 0)
msg.add(b'89', 8)
msg.add(b'01', 0)
msg.add(b'23', 2)
msg.add(b'67', 6)
assert msg.is_complete() == True
assert msg.reconstruct() == b'0123456789'
print("passed")


print("out of bounds: ", end='')
msg = ip.FragmentedMessage(10)
msg.add(b'a' * 10, 1)
msg.add(b'b' * 2, 2)
msg.add(b'23', 2)
msg.add(b'89', 8)
msg.add(b'45', 4)
msg.add(b'ab', 10)
msg.add(b'67', 6)
msg.add(b'45', 4)
msg.add(b'01', 0)
msg.add(b'89', 8)
msg.add(b'01', 0)
msg.add(b'23', 2)
msg.add(b'67', 6)
assert msg.is_complete() == True
assert msg.reconstruct() == b'0123456789'
print("passed")

print("Defragmenter tests:")


