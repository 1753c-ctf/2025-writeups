# Escatlate
### There are two flags to find in this challenge. Let's take a look at how to find them.
[https://escatlate-52bc47e034fa.1753ctf.com/]
>Challenge description
>
>During my travels I met a lot of interesting cats and you get to know them too, they are great but don't check who they bring into their gang. Make friends with them give them advice comment on their appearance, have fun!!!!
## Moderator

Logging in to the cat site automatically gets the *user role*, it allows you to browse the cat site and post comments. However, the application has a vulnerability: Mass Assignment. This means that the role assignment is not checked and the user can change it.That is, by providing a session token we are able to overwrite our role. Read more [here](https://tcm-sec.com/exploiting-mass-assignment-vulnerabilities/)

```bash 
example solution


```
## Admin

