# dgltool

The goal of this tool is to help automate the unexciting parts of playing
NetHack on public servers.  Use this tool to connect to [Dungeon Game
Launch][dgl] instances with a single command.

[dgl]: https://nethackwiki.com/wiki/Dgamelaunch

## Features

- A configuration file to describe SSH and `DGLAUTH` environment settings.
- Simple full-match aliases to connect to an account.

## Wishlist

- Commands to back up and restore configs
- Option to run game session in tmux session
- Or some other way to introduce game macros or scripting.

## Configuration file format

Example:

```toml
[[account]]
aliases = ["identifiers", "for", "this", "account"]
dgl.user = "Your DGL username"
dgl.password = "Your DGL password"
ssh.user = "nethack"  # SSH user
ssh.host = "hardfought.org"  # SSH Server
```

## FIXME

```
error: builder for '/nix/store/jvcidwk9kpka52cwcqpfjaim0kh8a64p-python3.10-xdg-base-dirs-6.0.0.drv' failed with exit code 2;
       last 10 log lines:
       >   File "<frozen importlib._bootstrap>", line 1050, in _gcd_import
       >   File "<frozen importlib._bootstrap>", line 1027, in _find_and_load
       >   File "<frozen importlib._bootstrap>", line 992, in _find_and_load_unlocked
       >   File "<frozen importlib._bootstrap>", line 241, in _call_with_frames_removed
       >   File "<frozen importlib._bootstrap>", line 1050, in _gcd_import
       >   File "<frozen importlib._bootstrap>", line 1027, in _find_and_load
       >   File "<frozen importlib._bootstrap>", line 1004, in _find_and_load_unlocked
       > ModuleNotFoundError: No module named 'poetry'
       >
       >
       For full logs, run 'nix log /nix/store/jvcidwk9kpka52cwcqpfjaim0kh8a64p-python3.10-xdg-base-dirs-6.0.0.drv'.
error: 1 dependencies of derivation '/nix/store/cy2x3wkc7yqnmmz5nfhwqgbw3b2w21x2-python3.10-dgltool-0.0.1.drv' failed to build
```

(Hence this tool doesn't pull in xdg_base_dirs...)

## License

AGPL-3.0

## Why?

This is a rewrite of [ssh-hack][ssh-hack] in Python which gives us a few benefits:

1. Better packaging support, especially within the Nix ecosystem
2. More contributors know Python than Racket
3. Easier to maintain code - more batteries included, and a more mature
   language package manager (poetry vs raco).

[ssh-hack]: https://github.com/winny-/ssh-hack
