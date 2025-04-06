# Ancient Memory

📜 Category: _MISC_

> Old legends were right. We've found evidence of an ancient memory. Not sure how to extract the flag it’s supposed to remember, but this Python code might be a clue...

---

## Discovery

This challenge provides two files: `model.pt` and `train.py`. A quick look at the Python file reveals a script that trains an AI model. The script creates a `FlagSimilarityModel`, which checks how similar a provided flag is to the correct flag. The similarity is computed by comparing character-by-character positions between the candidate flag and the target flag.

The training data is processed in the `process_flags` function. For each flag in the input list, the flag is normalized to 26 characters (the expected flag length) by either truncating or padding with `'x'`. Then, the similarity score is computed by counting how many characters in the candidate flag match the correct flag at the exact positions. The ratio of correct characters to the flag length is used as the score.

With this information, we can reverse the process using the provided `model.pt`. The idea is to perform a greedy search:  
1. **Start with the known flag format.** The flag is known to start with `1753c{` and end with `}`.  
2. **Iteratively determine each unknown character.** For each position in the flag (excluding the known prefix and suffix), try all 128 ASCII characters. For each candidate letter, pad the remaining positions with a placeholder (e.g., `'?'`) and append the known suffix.  
3. **Choose the letter that results in the highest predicted similarity score.**  
4. **Repeat until all characters are determined.**

This reverse-engineering approach leverages the model's similarity scoring to gradually reconstruct the correct flag.

---

## Solution

Below is the final code used to reverse the process and extract the flag:

```python
import torch
import torch.nn as nn
import platform

FLAG_LENGTH = 26
PLACEHOLDER = '?'
KNOWN_PREFIX = "1753c{"
KNOWN_SUFFIX = "}"

# Define the model (same architecture as training)
class FlagSimilarityModel(nn.Module):
    def __init__(self):
        super(FlagSimilarityModel, self).__init__()
        self.model = nn.Sequential(
            nn.Linear(FLAG_LENGTH * 128, 256),
            nn.ReLU(),
            nn.Linear(256, 128),
            nn.ReLU(),
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Linear(64, 1),
            nn.Sigmoid()
        )
    
    def forward(self, x):
        return self.model(x)

def get_device():
    if torch.cuda.is_available():
        return torch.device("cuda")
    elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available() and platform.system() == 'Darwin':
        return torch.device("mps")
    else:
        return torch.device("cpu")

def one_hot_flag(flag):
    X = torch.zeros(FLAG_LENGTH, 128)
    for i, char in enumerate(flag):
        X[i, ord(char)] = 1
    return X.flatten().unsqueeze(0)

def main():
    device = get_device()
    model = FlagSimilarityModel().to(device)
    checkpoint = torch.load('model.pt', map_location=device)
    model.load_state_dict(checkpoint['model_state_dict'])
    model.eval()

    # Start with known prefix and reserve last char for known suffix
    current_flag = KNOWN_PREFIX
    total_unknown = FLAG_LENGTH - len(KNOWN_PREFIX) - len(KNOWN_SUFFIX)
    
    for pos in range(total_unknown):
        best_score = -1
        best_char = None
        for ascii_code in range(128):
            candidate_char = chr(ascii_code)
            candidate_flag = current_flag + candidate_char + (PLACEHOLDER * (total_unknown - pos - 1)) + KNOWN_SUFFIX
            x = one_hot_flag(candidate_flag).to(device)
            with torch.no_grad():
                score = model(x).item()
            if score > best_score:
                best_score = score
                best_char = candidate_char
        current_flag += best_char
        print(f"Found letter {len(current_flag) - len(KNOWN_PREFIX)}: '{best_char}' -> {current_flag}")

    # Append known suffix
    final_flag = current_flag + KNOWN_SUFFIX
    print("\nFinal flag:", final_flag)

if __name__ == "__main__":
    main()
```

---

Running it we get following results

```bash
$ python3 ./exploit.py
Found letter 1: 'w' -> 1753c{w
Found letter 2: 'r' -> 1753c{wr
Found letter 3: 'w' -> 1753c{wrw
Found letter 4: 't' -> 1753c{wrwt
Found letter 5: 't' -> 1753c{wrwtt
Found letter 6: '3' -> 1753c{wrwtt3
Found letter 7: 'n' -> 1753c{wrwtt3n
Found letter 8: '_' -> 1753c{wrwtt3n_
Found letter 9: '1' -> 1753c{wrwtt3n_1
Found letter 10: 'n' -> 1753c{wrwtt3n_1n
Found letter 11: '_' -> 1753c{wrwtt3n_1n_
Found letter 12: 'm' -> 1753c{wrwtt3n_1n_m
Found letter 13: 'y' -> 1753c{wrwtt3n_1n_my
Found letter 14: '_' -> 1753c{wrwtt3n_1n_my_
Found letter 15: 'b' -> 1753c{wrwtt3n_1n_my_b
Found letter 16: 'r' -> 1753c{wrwtt3n_1n_my_br
Found letter 17: 'a' -> 1753c{wrwtt3n_1n_my_bra
Found letter 18: '1' -> 1753c{wrwtt3n_1n_my_bra1
Found letter 19: 'n' -> 1753c{wrwtt3n_1n_my_bra1n

Final flag: 1753c{wrwtt3n_1n_my_bra1n}
```

Sounds just a bit off.. one letter does not look correct, but it is easy to guess that `1753c{writt3n_1n_my_bra1n}` is the correct flag. 

Probably if we would add some extra runs for each letter with different `PLACEHOLDER` value for each, pick the letter that was best for most provided placeholders then our code would end up printing correct flag every time. In this case it seemed to be far easier just to stick to "good enough" version of the script.
