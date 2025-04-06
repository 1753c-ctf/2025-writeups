# leakcan

🏴‍☠️ Category: _PWN_
    
> One of our agents never returned from his mission. We've found that he died captured by enemies. All that we got left are these backup files.

## Discovery

The Program is asking an user for a name and then for a country. You can easily overwrite whole buffer which is only 24 bytes long; 
Program is using the same buffer for name and country;
Program is using system call's read() and write();
Program provides a your_goal function which will print the flag;

High level code looks like that:

```
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>


int main() {

    char message1[] = "What's your name?\n\0";
    char message2[] = "Can you provide me with country also? I will save it\n\0";
    char message3[] = "Hello! \0";

    write(1, message1, strlen(message1));

    char buffer[24];
    read(0, buffer, 120);

    write(1, message3, strlen(message3));
    write(1, buffer, strlen(buffer));

    write(1, message2, strlen(message2));
    read(0, buffer, 120);

    printf("Data saved, thank you. Good luck in the challenge.\n");
    return 0;
}


void your_goal() {
    FILE *file;
    char buffer[256];

    file = fopen("./flag", "r");
    if (file == NULL) {
        perror("can not open the flag /flag");
        return;
    }

    while (fgets(buffer, sizeof(buffer), file) != NULL) {
        write(1, buffer, 40);
    }

    fclose(file);
}
```
Program is NO PIE which means that address of your_goal function will not be changes during runtime;
Program has a canary which is protecting from simply overwriting a return address with your_goal address;

```
RELRO           STACK CANARY      NX            PIE             RPATH      RUNPATH      Symbols         FORTIFY Fortified       Fortifiable     FILE
Partial RELRO   Canary found      NX enabled    No PIE          No RPATH   No RUNPATH   43 Symbols        No    0               2               ./chall

```


## Solution

The intended solution is to save and use stack protector called canary. If this is enabled, stack smashing is harder but still possible.
If the buffer is getting written two times in the row, we can split solution to two steps;

1) overwrite all bytes to the stack canary (including null byte) and print the canary;
2) overwrite return address with your_goal address but with canary included; 

ROP Chains are probably also possible as there is call rax gadget but I have not test full chain;


## Exploitation

The source code can be found in [solution.py](solution.py) file. After running it we get following output:

```
[DEBUG] Received 0x100 bytes:
    00000000  31 37 35 33  63 7b 63 34  6e 34 72 79  5f 31 66 5f  │1753│c{c4│n4ry│_1f_│
    00000010  74 68 33 72  33 27 35 5f  34 5f 6d 33  6d 5f 6c 33  │th3r│3'5_│4_m3│m_l3│
    00000020  34 6b 7d 0a  00 7f 00 00  40 20 02 14  f4 7f 00 00  │4k}·│····│@ ··│····│

```


b"1753c{c4n4ry_1f_th3r3'5_4_m3m_l34k}"
