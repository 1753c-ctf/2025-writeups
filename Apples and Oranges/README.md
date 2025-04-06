# 🍌 Apples and Oranges MISC

**Category:** MISC

> After capturing an enemy spy, the only thing we got from him was that the password is `bananafruit`. It does not seem to be right though. Can you help us?

---

## Overview

The challenge gives you a Node.js script that expects a password input through a network connection. However, it restricts the characters to a small allowed set: `+![]{}() `.

---

## How It Works

The trick is to use JavaScript type coercion and clever expressions to build the string `"bananafruit"` using only the allowed characters. This is based on the WTFJS trick. Each part of the expression extracts a character from an expression like `([]+{})` or `(![]+[])`, which converts JavaScript objects and booleans into strings, then picks specific characters using array-like indexing.

For example:
- `([]+{})` converts to the string `"[object Object]"`, and indexing into it can extract characters.
- `(![]+[])` converts to `"false"`.

By combining these and adding various arithmetic expressions like `+!![]` (which evaluates to `1`), you can create any string you want.

---

## The Working Solution

Here’s the final expression that produces `"bananafruit"`:

```js
([]+{})[(+!![]+ +!![])]+(![]+[])[+!![]]+(+{})+(![]+[])[+!![]]+(![]+[])[+[]]+(!![]+[])[+!![]]+(!![]+[])[(+!![]+ +!![])]+(([][[]]+[])[(+!![]+ +!![]+ +!![]+ +!![]+ +!![])])+(!![]+[])[+[]]
```

You can submit this expression via netcat:
```
nc apples-and-oranges-25b1895e82ba.tcp.1753ctf.com 12827
```

When the expression is evaluated, it returns `"bananafruit"`, and if it matches the expected password, the server prints the flag:  
`1753c{b4n4n4_1s_g00d_s0urc3_0f_pot4ss1um}`