# Luck

🍀 Category: _PWN_

> Lucky enough?
>
>nc luck-c87cea04b0d4.tcp.1753ctf.com 16448


## Discovery

This challenge provides nc port we can connect to and a source code for the app running there.

The source code seems to be split into two parts. First is checking if we are a human. This is just an mechanism to avoid bruteforce. 

The second one is a game where you play against joker. Rolling the dice you need to be first to get 100 points.

Problem is this part:

```csharp
var playerRoll = rng.Next(1, 7);
var jokerRoll = rng.Next(5, 7);
```

We can roll 1,2,3,4,5,6, but Joker can only roll 5 or 6. We need incredible luck to win.

The only thing that can save us is that the game asks for seed that is then used to run random number generator.

## Solution

Let's try to win the game then. We can figure out the correct RNG to run by brutforcing multiple possible seeds finding one that gives us victory:

```csharp
class Program
{
    public static async Task Main() 
    {
        while(true)
        {
            var seed = Guid.NewGuid().ToString();   
            var result = await Try(seed);
            if(result)
                break;
        }
    }

    static async Task<bool> Try(string seedInput)
    {  
        Console.WriteLine($"checking {seedInput}");

        var rng = new Random(GetSeed(seedInput));
            
        Console.WriteLine(string.IsNullOrWhiteSpace(seedInput) 
            ? "Using random seed." 
            : $"Using seed: {seedInput}");
        
        var playerScore = 0;
        var jokerScore = 0;
        
        while (playerScore < 100 && jokerScore < 100)
        {
            var playerRoll = rng.Next(1, 7);
            var jokerRoll = rng.Next(5, 7);

            playerScore += playerRoll;
            jokerScore += jokerRoll;
        }
        
        if (playerScore > jokerScore) return true;

        return false;
       
    }
    
    static int GetSeed(string? input)
    {
        if (string.IsNullOrWhiteSpace(input))
            return Environment.TickCount;

        var hash = SHA256.HashData(Encoding.UTF8.GetBytes(input));
        return BitConverter.ToInt32(hash, 0);
    }
}
```

We can run it and after working for a while it will stop giving us the winning seed:

```bash
$ dotnet run
...
Using seed: b2196c74-85d2-4fa3-b12b-0ba6b7e7071e
checking 341f35d3-afae-49a6-b999-e17a642abf3d
Using seed: 341f35d3-afae-49a6-b999-e17a642abf3d
checking f77c02ef-667a-4ef4-abc9-3df5d63672d5
Using seed: f77c02ef-667a-4ef4-abc9-3df5d63672d5
checking 81da198f-1986-4c50-a990-93218923c649
Using seed: 81da198f-1986-4c50-a990-93218923c649
checking f910d846-5061-429c-b3aa-8536c9785f62
Using seed: f910d846-5061-429c-b3aa-8536c9785f62
checking a93026a7-1d2d-4d82-a4e9-dadfa6641928
Using seed: a93026a7-1d2d-4d82-a4e9-dadfa6641928
checking a99be48d-16cc-45ac-82ba-cf744b932453
Using seed: a99be48d-16cc-45ac-82ba-cf744b932453
```

Let's try it then:

```bash
Enter a game seed (or press Enter for random): a99be48d-16cc-45ac-82ba-cf744b932453
Using seed: a99be48d-16cc-45ac-82ba-cf744b932453

Current scores - You: 0, Joker: 0
Press Enter to roll...

You rolled: 5
Joker rolled: 5

Current scores - You: 5, Joker: 5
Press Enter to roll...

You rolled: 6
Joker rolled: 5

Current scores - You: 11, Joker: 10
Press Enter to roll...

You rolled: 5
Joker rolled: 6

Current scores - You: 16, Joker: 16
Press Enter to roll...

You rolled: 6
Joker rolled: 6

Current scores - You: 22, Joker: 22
Press Enter to roll...

You rolled: 6
Joker rolled: 5

Current scores - You: 28, Joker: 27
Press Enter to roll...

You rolled: 5
Joker rolled: 5

Current scores - You: 33, Joker: 32
Press Enter to roll...

You rolled: 5
Joker rolled: 5

Current scores - You: 38, Joker: 37
Press Enter to roll...

You rolled: 4
Joker rolled: 5

Current scores - You: 42, Joker: 42
Press Enter to roll...

You rolled: 6
Joker rolled: 6

Current scores - You: 48, Joker: 48
Press Enter to roll...

You rolled: 6
Joker rolled: 5

Current scores - You: 54, Joker: 53
Press Enter to roll...

You rolled: 4
Joker rolled: 5

Current scores - You: 58, Joker: 58
Press Enter to roll...

You rolled: 6
Joker rolled: 5

Current scores - You: 64, Joker: 63
Press Enter to roll...

You rolled: 5
Joker rolled: 5

Current scores - You: 69, Joker: 68
Press Enter to roll...

You rolled: 6
Joker rolled: 5

Current scores - You: 75, Joker: 73
Press Enter to roll...

You rolled: 5
Joker rolled: 6

Current scores - You: 80, Joker: 79
Press Enter to roll...

You rolled: 4
Joker rolled: 5

Current scores - You: 84, Joker: 84
Press Enter to roll...

You rolled: 5
Joker rolled: 5

Current scores - You: 89, Joker: 89
Press Enter to roll...

You rolled: 6
Joker rolled: 5

Current scores - You: 95, Joker: 94
Press Enter to roll...

You rolled: 6
Joker rolled: 6

Arrhhhh.. You beat me.. how
Here's your flag: 1753c{wh4t_4n_1ncred1ble_luck_1t_w4sss}
Press Enter to exit...
```