#!/usr/bin/env python3
# https://bughunters.google.com/blog/5424842357473280/zen-and-the-art-of-microcode-hacking

import json
from itertools import batched
from Crypto.Hash import CMAC
from Crypto.Cipher import AES
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
from Crypto.Util.number import isPrime

cmac_key = bytes.fromhex('2b7e1516 28aed2a6 abf71588 09cf4f3c')
pubkey_tag = bytes.fromhex('01807bc2cef4a141a76e2b50ba1b9264')
e = 0x10001

def xor(b0, b1):
    return bytes(a ^ b for a, b in zip(b0, b1))

def chunked(msg):
    return [bytes(chunk) for chunk in batched(msg, 16)]

def cmac_derive_key(k):
    C = 0x87
    key_len = 128
    key_mask = 2**key_len - 1
    k_int = int.from_bytes(k)
    kn = k_int << 1
    if kn > key_mask:
        kn = kn & key_mask ^ C
    return kn.to_bytes(16)


def cmac_derive_keys(k, cipher):
    k0 = cipher.encrypt(b'\x00' * 16)
    k1 = cmac_derive_key(k0)
    k2 = cmac_derive_key(k1)
    return (k1, k2)

def cmac_padding(padding_len):
    if padding_len == 0:
        return b''
    zeros_len = padding_len - 1
    return b'\x80' + b'\x00' * zeros_len

def cmac_pad(block):
    return block + cmac_padding(16 - len(block))

def cmac_tweak_last_block(block, key, cipher):
    k1, k2 = cmac_derive_keys(key, cipher)
    tweak_key = k1 if len(block) == 16 else k2
    block = cmac_pad(block)
    return xor(block, tweak_key)

def cmac2(msg, key):
    cipher = AES.new(cmac_key, mode=AES.MODE_ECB)
    blocks = chunked(msg)
    normal_blocks = blocks[:-1]
    last_block = blocks[-1]
    output = b'\x00' * 16
    for block in normal_blocks:
        output = cipher.encrypt(xor(block, output))
    last_block = cmac_tweak_last_block(last_block, key, cipher)
    return cipher.encrypt(xor(last_block, output))

def mac(msg, key):
    cmac = CMAC.new(key, ciphermod=AES)
    cmac.oid = '2.16.840.1.101.3.4.2.42'
    cmac.update(msg)
    return cmac

def cmac_match(msg, key, target_cmac):
    '''
    make msg match target_cmac by changin next to last block
    '''
    cipher = AES.new(key, mode=AES.MODE_ECB)

    blocks = chunked(msg)
    normal_blocks = blocks[:-2]
    second_last_block = blocks[-2]
    last_block = blocks[-1]

    target_last_pt = cipher.decrypt(target_cmac)

    last_block_tweaked = cmac_tweak_last_block(last_block, key, cipher)

    target_second_last_ct = xor(target_last_pt, last_block_tweaked)

    target_second_last_pt = cipher.decrypt(target_second_last_ct)

    output = b'\x00' * 16
    for block in normal_blocks:
        output = cipher.encrypt(xor(block, output))

    second_last_block = xor(output, target_second_last_pt)

    all_blocks = normal_blocks + [second_last_block, last_block]

    new_msg = b''.join(all_blocks)

    assert mac(new_msg, key).digest() == target_cmac

    return new_msg


payload = bytearray(b'\x00' * 16)

zeros_mac = mac(payload, cmac_key).digest()
zeros_mac2 = cmac2(payload, cmac_key)
print(f'{zeros_mac.hex()=}')
print(f'{zeros_mac2.hex()=}')
assert zeros_mac == zeros_mac2

def divides(factor, compound):
    return compound // factor * factor == compound


def is_nice_key(n, biggest_small_prime=0xff):
    small_primes = [p for p in range(biggest_small_prime) if isPrime(p)]
    for p in small_primes:
        if divides(p, n):
            q = n // p
            if isPrime(q):
                try:
                    d = pow(e, -1, (p-1)*(q-1))
                    return p, q, d
                except ValueError: pass

get_nice_key = is_nice_key

def make_update(p, q, d):
    n = p*q
    key = RSA.construct((n, e, d, p, q))
    signer = pkcs1_15.new(key)
    payload = b'Gimmie a flag, pretty please.'
    signature = signer.sign(mac(payload, cmac_key))
    update = {
        'payload': payload.hex(),
        'pubkey': hex(n)[2:],
        'signature': signature.hex(),
    }
    print(json.dumps(update))

for i in range(2**8):
    n_len_bits = 2048
    n_len_bytes = n_len_bits // 8
    n = 2**(n_len_bits-1) + (2*i + 1)

    n_bytes = n.to_bytes(n_len_bytes)

    n_bytes = cmac_match(n_bytes, cmac_key, pubkey_tag)
    n = int.from_bytes(n_bytes)
    if is_nice_key(n):
        p, q, d = get_nice_key(n)
        print(f'{hex(n)} =')
        print(f'{hex(p)} * {hex(q)}')
        print(f'{hex(d)}')
        try:
            make_update(p, q, d)
            break
        except ValueError:
            continue
