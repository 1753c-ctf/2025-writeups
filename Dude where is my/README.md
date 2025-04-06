# Dude where is my

🧑‍💻 Category: _OSINT_

> I'm not sure where I lost my car, but I believe I’ll remember if I can see the original photo again. Can you find it? I only have this photoshopped and cropped version, but I’m confident it contains enough information for an OSINT expert. To prove your success, submit a flag with the Build Number from the EXIF data in the format: `1753c{Build Number}`.

![car.jpg](car.jpg)

## Discovery

We can already see that simply reverse searching for this image on google, bing or yandex wont work, besause the image is damaged on purpose. We need to find another key. 

## Solution

It is right in front of you, on the front window. There is a sticker in the bottom-right corner with the registration number of this car. It is not very clear, but with some confidence, we can identify the characters: `WWY1527`.  

We can also see that this car is Polish (there is a Polish flag on the left and... well, this CTF is hosted by Polish people). By looking at Polish registration numbers, we know that one character is missing — that's a place for guessing.  

Now, you can either use Google to check all available characters or go straight to [tablica-rejestracyjna.pl](https://tablica-rejestracyjna.pl/), an awesome Polish website for unlocking your post-driving rage. On this site, people mostly leave mean and angry comments about other drivers, connecting them to their car registration numbers.  

So, we can construct this URL:  

```
https://tablica-rejestracyjna.pl/WWY1527${missing}
```

Then, iterate through all digits and letters until we find the full registration and our car:  

```
WWY15270
```

![20250310132833.jpg](20250310132833.jpg)


(By the way, I have no idea who the owner is.) Googling it will give us the same result.  

Now, the cool thing: Apparently, the owners of this service are not stripping the uploaded images of any EXIF information...  

Now, the last step is to extract the **build number** from the EXIF data of the full car image:  


```bash
$ exiftool 20250310132833.jpg | grep "Build Number"
Build Number                    : S2RUBS32.51-15-3-19
```

`S2RUBS32.51-15-3-19` wrapped with `1753c{...}` is the correct flag for this challenge.
