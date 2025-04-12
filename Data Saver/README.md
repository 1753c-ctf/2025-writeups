### Data saver

In `process_message()`, there is an underflow in calculating `data_no_footer_length` - passing 0 (or any value below 4) allows reading and writing
pretty much entire stack.

It is possible to:
 - read stack,
 - retrieve canary and some known libc address,
 - write back canary followed by a rop chain.

While it's not obvious from the source that copying ~2^16 bytes is possible, it can be verified by sending `OP_PING` with `data_length` set to 0
and veryfying that server is in fact able to `write()` that much.

While not relevant to solvability of the challenge, there's an interesting difference between functions like `memcpy` and syscalls like `read`/`write` when end of the passed buffer isn't accessible:
memcpy (or any userspace function) accessing unmapped memory results in a segfault, while when reading/writing kernel does as much as it can, and then just returns
(probably reporting an error?) when encountering unmapped page.
