## Update

The challenge is based on crypto from amd "entrysign" vulnerability (CVE-2024-56161).
Here's a nice writeup of entrysign itself (solution to the challenge is pretty much identical): https://bughunters.google.com/blog/5424842357473280/zen-and-the-art-of-microcode-hacking

The weakness of the signature scheme is based on the fact that CMAC (https://en.wikipedia.org/wiki/One-key_MAC) is used as a hash function, and key to that mac is retrievable.

With the cmac key it's possible to create almost arbitrary collisions of the cmac. With a bit of trial and error it's fairly easy to find key that collides with original key and is easily factorable, which can then be used to sign arbitrary data.
