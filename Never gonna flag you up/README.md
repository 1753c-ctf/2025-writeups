# Never gonna flag you up

🎹 Category: _STEGANO_

> I always wanted to do this song arrangement! I hope you will rate it 10 out of 10!


## Discovery

The challenge includes a MIDI file with some recorded notes.

First, we'll check the file with hidden messages in 'Program Change':
- https://github.com/maxcruz/stegano_midi

We've got output written in base64: `MTc1M2N7RmFrZV9GbGFnfQ==`

Unfortunately, it's a fake flag: `1753c{Fake_Flag}`

Let's check this file in popular app Audacity:

![alt text](<audacity.png>)

Everything looks quite normal. 

So let's dig deeper. Unless you've got a professional DAW, here's another approach for discovery:

```python
import mido
from collections import Counter

midi_filename = "final_version_v199237.mid"

mid = mido.MidiFile(midi_filename)

notes = []

for track in mid.tracks:
    for msg in track:
        if msg.type == 'note_on' and msg.velocity > 0:
            notes.append((msg.note, msg.velocity))

print("Notes and velocities:")
for note, velocity in notes:
    print(f"Note: {note}, Velocity: {velocity}")
```
After running this script, you can see that most common velocity is 81 so let's filter it out!

## Solution

```python
import mido
from collections import Counter

midi_filename = "final_version_v199237.mid"

mid = mido.MidiFile(midi_filename)

notes = []

for track in mid.tracks:
    for msg in track:
        if msg.type == 'note_on' and msg.velocity > 0:
            notes.append((msg.note, msg.velocity))

velocity_counts = Counter(velocity for _, velocity in notes)

if velocity_counts:
    most_common_velocity, count = velocity_counts.most_common(1)[0]
    print(f"Most common velocity: {most_common_velocity} ({count} times)")

filtered_velocity = [];
for note, velocity in notes:
    if velocity != most_common_velocity:
        filtered_velocity.append(velocity)
print("Filtered velocities:")
print(filtered_velocity)
```

After running this, we can see that we’ve got some info:

```
Most common velocity: 81 (202 times)
Filtered velocities:
[64, 49, 55, 53, 51, 99, 123, 82, 105, 99, 107, 95, 65, 115, 116, 108, 101, 121, 95, 73, 115, 95, 80, 114, 111, 117, 100, 95, 79, 102, 95, 89, 111, 117, 125]
```
If we treat this as charcode (base 10) input:

```python
flag = ''.join(chr(code) for code in filtered_velocity)
print("Flag:")
print(flag)
```
We've got a flag! `1753c{Rick_Astley_Is_Proud_Of_You}`