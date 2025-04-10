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

flag = ''.join(chr(code) for code in filtered_velocity)
print("Flag:")
print(flag)
