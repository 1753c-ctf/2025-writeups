# Free flag

🤷‍♂️ Category: _WEB/CRYPTO_
🔗 Url: https://free-flag-2e5714cdf314.1753ctf.com

> Well, this task worked for me before the CTF, but now it seems to be broken. I will fix it on Monday, I promise.

## Discovery

Website shows flag, but all the inner characters seems to be scrambled. Looking into the source we can find a script responsible for populating the flag:

```html
<script>
        async function getFlag() {
            const flag = [0x45, 0x00, 0x50, 0x39, 0x08, 0x6f, 0x4d, 0x5b, 0x58, 0x06, 0x66, 0x40, 0x58, 0x4c, 0x6d,0x5d, 0x16, 0x6e, 0x4f, 0x00, 0x43, 0x6b, 0x47, 0x0a,0x44, 0x5a, 0x5b, 0x5f, 0x51, 0x66, 0x50, 0x57]
            const tz = Intl.DateTimeFormat().resolvedOptions().timeZone;
            const resp = await fetch("https://timeapi.io/api/time/current/zone?timeZone=" + tz);
            const date = await resp.json();
            const base = date.timeZone + "-" + date.date + "-" + date.time;
            var hash = CryptoJS.MD5(base).toString();

            const result = flag.map((x, i) => String.fromCharCode(x ^ hash.charCodeAt(i))).join('')
            document.querySelector('span').innerText = result;

            document.getElementsByClassName('ready')[0].style.display = 'block';
            document.getElementsByClassName('loading')[0].style.display = 'none';
        }

        getFlag();
    </script>
```

It looks that the flag is calculated based on the current date/time information which can explain why the flag was working before, but now it fails to display correctly.

Looking into the script it seems to do following steps:

1) Get date/time information from API
2) Generates base for hash combining timezone, date, and time info
3) XOR's bytes stored in "flag" variable with the generated hash
4) Prints the result inside 1753c{...} wrapper

## Solution

Since we know the flag worked correctly at some point in time we can run the code ourselves trying to locally brute force all possible date/time combinations starting at CTF start time and going back until the correct flag will be displayed.

Assuming we can go a few months back there is _~100_ days to cover, each with _1440_ minutes. This gives us _~144000_ combinations which should be fairly easy to brute force.

The timezone parameter is unknown, but doing a little research about the 1753c team we can assume that the author is from Poland and the timezone should be set to _Europe/Warsaw_.

As running such script might generate a lot of false flags, we can narrow down the list by displaying only results that are made of printable characters allowed in the flag.

## Exploitation

To exploit we can use the same code running as a node program. The source code can be found in [exploit.js](exploit.js) file. After running it we get following output:

```
v3dZ9_u8=7Pqmz\it^x3q\whrjoj3Uin
s0`]iYukk?QxnxThrZz3s^v:}nj=4P4a
}62Z8Xtb;3_v;{Yjp^ybv_p<vki<cRg1
ve5\j_ynncQt`u^lu]z7s_t?u<>;5V4c
te3Xi^{ll0Usmu]nrXz7wXp;q<9kh^e3
s5eX?[xil?_vn}]8u^}4rRtor?mk`Vie
see_i_told_you_it_was_working_b4
|2dZ1Xy9lgWtaxYdwX{7tYu:vnlg2U``
v1h\=[xoj3^s;{Uou\|5qSp=ubhg5V2`
qch_j\|b>cRw:|_hu\|4rZu9woj=hP5o
```

when `see_i_told_you_it_was_working_b4` wrapped with `1753c{...}` is the correct flag for this challenge.