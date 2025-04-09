# Escatlate
### There are two flags to find in this challenge. Let's take a look at how to find them.
[https://escatlate-52bc47e034fa.1753ctf.com/]
>Challenge description
>
>During my travels I met a lot of interesting cats and you get to know them too, they are great but don't check who they bring into their gang. Make friends with them give them advice comment on their appearance, have fun!!!!
## Moderator

Logging in to the cat site automatically gets the `user role`, it allows you to browse the cat site and post comments. However, the application has a vulnerability: Mass Assignment. This means that the role assignment is not checked and the user can change it.That is, by providing a session token we are able to overwrite our role. Read more [here](https://tcm-sec.com/exploiting-mass-assignment-vulnerabilities/)

```bash 
example solution


```
## Admin

However, with the second flag, i.e. changing the role from `user` to `admin`, the application has a dotless vulnerability. When you specify a new role as `admın`, Unicode case collisions happen and it is read as `ADMIN`. More information [here](https://dev.to/jagracey/hacking-github-s-auth-with-unicode-s-turkish-dotless-i-460n)

```bash 
example solution


```
