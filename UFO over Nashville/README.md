# UFO over Nashville

🧑‍💻 Category: _OSINT_

> In October 2020, Mark created a video using Adobe Premiere Pro, which he later uploaded to Parler. The video, less than a minute long, showcases a mesmerizing UFO spectacle. Within the footage, a neon sign welcomes visitors to a restaurant. We need to find out what they are serving for $3. Oh, one more thing: We are fairly certain that while creating this video, he used a file named ufo_over_nashville.mp4. The flag is in a form similar to this: 1753c{osint_challenge}

## Discovery

This challange is about two things: metadata and data leaks, in this case Parler data leak, that is hosted on the DDoSecrets platform. Start by downloading the leaked Parler video dataset from:

[https://ddosecrets.com/article/parler](https://ddosecrets.com/article/parler)

We do not need to download the whole gigantic leak, just the archive with the metadata. These files include detailed exif metadata such as GPS coordinates, device info, and more. And we will find within almost everything we need.

Use a command-line tool like `grep` to search through the metadata files. We will grep for the phrase `ufo_over_nashville.mp4` and find the videos that are shorter than 1 minute.

- `meta-OVGzl7txWOUA.json`
- `meta-BUcWJq4i1WHd.json`
- `meta-Ogfy1F4vu1qT.json`


Once you've found the metadata, download the related video. If you're using `meta-OVGzl7txWOUA.json`, then the corresponding video is likely named:

```
OVGzl7txWOUA.mp4
```

Open the video in any media player. Pay attention to visual elements in the footage.

You’ll spot a **neon sign** that points to:

👉 [https://robertswesternworld.com/honky-tonk-grill/](https://robertswesternworld.com/honky-tonk-grill/)

On this site look for menu. You will see in it that Moon Pie is for $3. 

## Solution

The flag is `1753c{moon_pie}`
