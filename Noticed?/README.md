# Noticed?

👀 Category: _OSINT_

> You are special, aren't you?
> You always felt it.
> The force accumulating at the tips of your fingers
> when you touch the keyboard.
> That's when the magic happens.
> Don't hold it back.
> Use it.

## Discovery

The text sounds familiar. 1753CTF was advertised with the teaser, where the voice behind the screen was telling exactly these words.

[1753 CTF - Teaser](https://www.youtube.com/watch?v=yRghHj9dkoo)

The teaser also appeared on the main #announcements channel on 1753CTF Discord server.

## Solution

Since we should notice something, then we should take a look at the video. Maybe the flag is just in there?

Tools like https://y2down.cc/ can help downloading the MP4 file containing the video.

Next we need to extract all frames from the video, hoping one or some of them will contain a flag. We can do that using `ffmpeg`

```bash
$ $fmpeg -i teaser.mp4 -vf "fps=1" frames/out%04d.png
```

Well, the number of frames is huge. Over 1600 pictures. Too much to look at, but we can use another tool - OCR named `tesseract`

```bash
$ for file in frames/*.png; do tesseract "$file" stdout >> results.txt; done
```

It takes a moment, but after a while we got results.txt file we can check. It contains a bunch of crap, but using `grep` we can get our flag:


```bash
$ cat results.txt | grep 1753c{
1753c{i_b3c4m3_a_h4ck3r}
```
