# Basecally a flag

🧑‍💻 Category: _CRYPTO_

> We've intercepted a Telegram chat that seems to involve the exchange of highly sensitive secrets. But where is the hidden information? We need our best experts to uncover it!

## Discovery

The flag is hidden in the 😎󠄡󠄧󠄥󠄣󠅓󠅫󠅤󠅘󠅕󠅏󠅧󠄠󠅢󠅜󠅔󠅏󠅙󠅣󠅏󠅝󠄠󠅢󠅕󠅏󠅑󠅞󠅔󠅏󠅝󠄠󠅢󠅕󠅏󠅙󠅞󠅣󠄤󠅞󠅕󠅏󠅢󠅕󠅓󠅕󠅞󠅤󠅜󠅩󠅭  emoji. How is it possible? 

This challenge is inspired by a recent [blog](https://paulbutler.org/2025/smuggling-arbitrary-data-through-an-emoji/) on Pauls Butler blog about smuggling arbitrary data through an emoji. 

The hidden message is embedded in an emoji and you can decode it using the online tool here: [https://emoji.paulbutler.org/?mode=decode](https://emoji.paulbutler.org/?mode=decode). Alternatively, you can write a decoder yourself. The key point is how to find out where to look for the flag in the first place. How do you even do that? This is the fun part, you have to figure it out somehow, this is spy level stegonagrapy 😎.

Anyway, have a look at this:

```python
"😎".encode('utf-8').hex() # Normal emoji
'f09f988e'

"😎󠄡󠄧".encode('utf-8').hex() # Emoji with payload
'f09f988ef3a084a1f3a084a7f3a084a5f3a084a3f3a08593f3a085abf3a085a4f3a08598f3a08595f3a0858ff3a085a7f3a084a0f3a085a2f3a0859cf3a08594f3a0858ff3a08599f3a085a3f3a0858ff3a0859df3a084a0f3a085a2f3a08595f3a0858ff3a08591f3a0859ef3a08594f3a0858ff3a0859df3a084a0f3a085a2f3a08595f3a0858ff3a08599f3a0859ef3a085a3f3a084a4f3a0859ef3a08595f3a0858ff3a085a2f3a08595f3a08593f3a08595f3a0859ef3a085a4f3a0859cf3a085a9f3a085ad'
```

## Solution

The flag is `1753c{the_w0rld_is_m0re_and_m0re_ins4ne_recently}`
