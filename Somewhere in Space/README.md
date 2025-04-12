# Somewhere in Space

👨‍🚀 Category: _OSINT_

> This handsome man is looking at a beautiful woman.  
> The flag is a filename in which the woman face is stored. Use only characters that are at least in 90% visible.  
> _Flag format: 1753c{filename}_

## Solution

The image can be easily found with Google image search.

One of the pages found this way contains all the graffiti:
- https://vagabundler.com/cyprus/streetart-map-limassol/agiou-andreou-253/

On few of the photos we can see that on the opposite of the astronaut, there is a bust of some lady:
- https://vagabundler.com/wp-content/uploads/2022/12/DSCN9466-1024x768.jpg

On some other photos we see it's Aphrodite's picture saved in a file:
- https://vagabundler.com/wp-content/uploads/2022/12/DSCN9441-1024x768.jpg

The filename can be seen only partially: `Aphrodite_final.j`

As the challenge description states that only characters visible in at least 90% should be used, tha flag is:

`1753c{Aphrodite_final.j}`
