# Sanity Check

🪦 Category: _FORENSIC_

> One of our agents never returned from his mission. We've found that he died captured by enemies. All that we got left are these backup files. Not sure how to get to them, but I think he used one of his family member names to secure it.


## Discovery

Challenge includes a folder name backup with some files and folders. The structure is nothing too familiar, but after googling all the folder names "data index keys locks snapshot" first result is documentation to a backup tool named Restic.

After installing restic we can try to open the backup with following command

```bash
$ restic -r backup snapshots
```

but what we get in return is

```bash
enter password for repository:
```

Well, kind of expected. Now how do we crack it open?

## Solution

The obvious first thought is, that since these files are on our local machine we try to bruteforce it. This repository seems to do what we want https://github.com/juergenhoetzel/restic-bruteforce.

This tool needs to be built from source using attached meson configuration

```bash
$ meson setup builddir && cd builddir && meson compile
```

Then we can grab neessary encryption information from backup folder

```bash
$ jq < keys/608e4fa104ef6b656198bc470f980ab147662d6dd7032855b3d04ce399fc9a0b 
{
  "created": "2025-04-06T17:07:05.806434091Z",
  "username": "root",
  "hostname": "f834fc6fec8b",
  "kdf": "scrypt",
  "N": 32768,
  "r": 8,
  "p": 7,
  "salt": "vTvkPe/DpBiHfQ4Hp4loPfnx4Wu1vZR0ZCtf1SMCki5j8xaFXH7uopJkhdBrwNlYEqpjr5TH6Gh3zDgYEIRUCg==",
  "data": "53yWN39gmUZSiqOgdI4JxZ/9xxBhwP/zW144NqYFRvtObK2FwVQDHQpQt0uQNxvEqhHeKL45eLj/HH+aK6LXu/OKWII3Olk+5v3Sfvu0whCngKDFFDgWfPPMgT5oErujVTg2FEe+gu3a2OKRlQNBg9fT/Q6DJKd18MnzAhy57l71NSs9AtjoOjgVngxa/0q2MKzUALEiQC66UTL03vVZYw=="
}
```

and use that data to run code cracking.

We just need a good dictionary of names. First one that google suggests is https://raw.githubusercontent.com/huntergregal/wordlists/refs/heads/master/names.txt. Let's try this one.

Now we need to run restic-bruteforce and be a little patient as it's not that fast:

```bash
$ time ./restic-brute -v -n 32768 -r 8 -p 7 vTvkPe/DpBiHfQ4Hp4loPfnx4Wu1vZR0ZCtf1SMCki5j8xaFXH7uopJkhdBrwNlYEqpjr5TH6Gh3zDgYEIRUCg== 53yWN39gmUZSiqOgdI4JxZ/9xxBhwP/zW144NqYFRvtObK2FwVQDHQpQt0uQNxvEqhHeKL45eLj/HH+aK6LXu/OKWII3Olk+5v3Sfvu0whCngKDFFDgWfPPMgT5oErujVTg2FEe+gu3a2OKRlQNBg9fT/Q6DJKd18MnzAhy57l71NSs9AtjoOjgVngxa/0q2MKzUALEiQC66UTL03vVZYw== <names.txt
```

Which outputs this and after a few minutes finds a password:

```bash
Using parameters (N=32768, r=8, p=7) on 4 Threads
Checked 32 passwords
Checked 60 passwords
Checked 92 passwords
Checked 120 passwords
Checked 152 passwords
Checked 180 passwords
Checked 212 passwords
Checked 240 passwords
Checked 269 passwords
Checked 300 passwords
Checked 328 passwords
Checked 360 passwords
Checked 388 passwords
Checked 420 passwords
Checked 448 passwords
Checked 478 passwords
Checked 508 passwords
Checked 537 passwords
Checked 568 passwords
Checked 597 passwords
Checked 628 passwords
Checked 657 passwords
Checked 688 passwords
Checked 717 passwords
Checked 747 passwords
Checked 777 passwords
Checked 806 passwords
Checked 837 passwords
Checked 866 passwords
Checked 896 passwords
Checked 926 passwords
Checked 955 passwords
Checked 986 passwords
Checked 1015 passwords
Checked 1046 passwords
Checked 1075 passwords
Checked 1106 passwords
Checked 1135 passwords
Checked 1165 passwords
Checked 1195 passwords
Checked 1225 passwords
Checked 1254 passwords
Checked 1283 passwords
Checked 1314 passwords
Checked 1343 passwords
Checked 1373 passwords
Checked 1403 passwords
Checked 1433 passwords
Checked 1463 passwords
Checked 1493 passwords
Found: Christopher

real	4m14.304s
user	16m35.819s
sys	0m20.692s
```

Christopher, eh? Now we can try to look into restic repository

```bash
$ restic -r backup --password-command "echo Christopher" snapshots
repository 83c0e793 opened (version 2, compression level auto)
created new cache in /Users/lukaszwronski/Library/Caches/restic
ID        Time                 Host        Tags        Paths  Size
------------------------------------------------------------------
389a509c  2025-04-06 20:02:12  AgentAlpha              /flag  16 B
------------------------------------------------------------------
1 snapshots
```

That show's us just one snapshot and we can check what files it contains with this command

```bash
$ restic -r backup --password-command "echo Christopher" ls 389a509c
repository 83c0e793 opened (version 2, compression level auto)
[0:00] 100.00%  4 / 4 index files loaded
snapshot 389a509c of [/flag] at 2025-04-06 18:02:12.182221879 +0000 UTC by root@AgentAlpha filtered by []:
/flag1.txt
/flag5.txt
```

Flag files sounds like a jackpot, but when printing them we get a fake flag?

```bash
$ restic -r backup --password-command "echo Christopher" dump 389a509c /flag1.txt
repository 83c0e793 opened (version 2, compression level auto)
[0:00] 100.00%  4 / 4 index files loaded
1753c{fake%      

$ restic -r backup --password-command "echo Christopher" dump 389a509c /flag5.txt
repository 83c0e793 opened (version 2, compression level auto)
[0:00] 100.00%  4 / 4 index files loaded
_flag}%  
```

Looks like flags 2 - 4 are missing. Fortunately Restic allows to restore deleted snapshots if only someone forgot to rune `prune` command. We can recover and then rebuild index lke this

```bash
$ restic -r backup --password-command "echo Christopher" recover

repository 83c0e793 opened (version 2, compression level auto)
load index files
[0:00] 100.00%  1 / 1 index files loaded
load 4 trees
[0:00] 100.00%  4 / 4 trees loaded
load snapshots
done

found 3 unreferenced roots
saved new snapshot d4efceea

$ restic -r backup --password-command "echo Christopher" repair index
```

and then when running snapshot list we see 2, not just 1 snapshot.

```bash
repository 83c0e793 opened (version 2, compression level auto)
ID        Time                 Host                          Tags        Paths     Size
---------------------------------------------------------------------------------------
389a509c  2025-04-06 20:02:12  AgentAlpha                                /flag     16 B
d4efceea  2025-04-06 20:25:21  MacBook-Air.local  recovered   /recover
---------------------------------------------------------------------------------------
2 snapshots
```

Now ls command shows us all recovered files

```bash
$ restic -r backup --password-command "echo Christopher" ls d4efceea
repository 83c0e793 opened (version 2, compression level auto)
[0:00] 100.00%  1 / 1 index files loaded
snapshot d4efceea of [/recover] at 2025-04-06 20:25:21.437775 +0200 CEST by hacker@MacBook-Air.local filtered by []:
/405d9e38
/405d9e38/flag1.txt
/405d9e38/flag2.txt
/405d9e38/flag3.txt
/405d9e38/flag4.txt
/405d9e38/flag5.txt
/a5170404
/a5170404/flag1.txt
/a5170404/flag3.txt
/a5170404/flag4.txt
/a5170404/flag5.txt
/c9663b07
/c9663b07/flag1.txt
/c9663b07/flag4.txt
/c9663b07/flag5.txt
```

and grabbing remaing flag parts we can get the full flag: `1753c{faked_my_own_death_to_save_the_flag}`

