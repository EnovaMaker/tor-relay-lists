# tor-relay-lists

**Plain-text lists of Tor relay addresses, rebuilt from the public network consensus.**

Independent reimplementation, written from the public Tor directory specification and from the
file names and layout that relay operators already use. No code from any other project.

```sh
python3 tor_relay_lists.py --out out/        # newest consensus from CollecTor
```

Each file has a three-line header (`Updated:`, a UTC time, a dashed line) and then one address per line.

| File | Contents |
|---|---|
| `relays-v4`, `relays-v6` | every relay in the consensus |
| `exits-v4`, `exits-v6` | relays with the Exit flag |
| `guards`, `hsdir`, `guard-exit`, `guard-hsdir-exit` | by flag |
| `authorities-v4`, `authorities-v6` | directory authorities |
| `above1-or`, `2-or`, `above2-or` (+ `-v6`) | addresses running 2+, exactly 2, or 3+ relays |

## Status

Checked on 19 Oct 2026 against a snapshot of an older, now-stopped list service taken on
30 Apr 2026 (the consensuses on either side of it): **98–100 %** of its addresses appear in the
matching list here. The remaining 1–2 % is ordinary churn between consensuses.

**Not yet covered:** overloaded relays, and Snowflake servers (the consensus does not carry either).

Not production-tested. MIT licensed.

## Where the lists are served

Every 30 minutes, at the repository root, under the same file names the older service used:

```
https://raw.githubusercontent.com/EnovaMaker/tor-relay-lists/main/guards.txt
```

**Moving from the older service: change the owner in the URL, nothing else.**
(`Enkidu-6` -> `EnovaMaker`.) A run that cannot fetch the consensus, or finds it implausibly
small, fails and leaves the previous lists in place.

Used by [`nixos-tor-anti-dos`](https://github.com/EnovaMaker/nixos-tor-anti-dos) (`lists.enable`)
and by [`tor-ddos-compat`](https://github.com/EnovaMaker/tor-ddos-compat).
