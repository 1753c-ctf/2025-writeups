# Basecally a flag

🧑‍💻 Category: _CRYPTO_

> To prevent industrial espionage, the development team devised their own secret method of communication. By using a custom encoding scheme, they ensured that only insiders could decipher their messages. However, one of their transmissions has been intercepted. Your task is to decode it and reconstruct the flag before it falls into the wrong hands. The flag is basecally in the attachement. To make a complete flag, you must put the result in 1753c{}.

The flag.txt content:

```
1100 1111 1110 1111 1100 1111 1100 1010 1001 1110 1011 1010 1010 1001 1110 1011 1001 1100 1100
```

## Discovery

Now this challenge is suppose not to be hard but tricky, but there is a hint in the title. It is no mistake that it is `basecally` not basically. What you are seeing is not a binary code. Is a quaternary code, thus it is using the digits 1, 2, 3, 4. BUT I've found all printable ASCII characters that can be written in quaternary code using only 1 and 0. 

Here is a function to convert decimal to quaternary:

```python
def to_base4(n):
    if n == 0:
        return "0"
    base4 = ""
    while n > 0:
        base4 = str(n % 4) + base4
        n //= 4
    return base4
```

to get all the printable characters that match our requrements:

```python
"".join(([i for i in string.printable if "3" not in str(to_base4(ord(i))) and "2" not in str(to_base4(ord(i)))]))
```

and the result is

```
ADEPQTU@
```

## Solution

To decode the flag we just have to reverse the process, and it is quite straightforward in python:

```python
"".join(chr(int(i, 4)) for i in "1100 1111 1110 1111 1100 1111 1100 1010 1001 1110 1011 1010 1010 1001 1110 1011 1001 1100 1100".split( ))
```

`PUTUPUPDATEDDATEAPP` wrapped with `1753c{...}` is the correct flag for this challenge.
