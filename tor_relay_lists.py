#!/usr/bin/env python3
"""Generate plain-text lists of Tor relay addresses from the public network consensus.

Standard library only. Writes one file per list, in the layout that relay operators already
consume: a three-line header, then one address per line.

    python3 tor_relay_lists.py --out out/                  # newest consensus from CollecTor
    python3 tor_relay_lists.py --consensus FILE --out out/ # a consensus you already have
"""
import argparse, os, re, sys, urllib.request
from collections import Counter
from datetime import datetime, timezone

COLLECTOR = "https://collector.torproject.org/recent/relay-descriptors/consensuses/"


def fetch_latest():
    idx = urllib.request.urlopen(COLLECTOR, timeout=60).read().decode()
    names = sorted(set(re.findall(r'href="(\d{4}-\d\d-\d\d-\d\d-\d\d-\d\d-consensus)"', idx)))
    if not names:
        sys.exit("no consensus listed at " + COLLECTOR)
    return urllib.request.urlopen(COLLECTOR + names[-1], timeout=120).read().decode("utf-8", "replace")


def parse(text):
    """Relays as dicts: ip (IPv4), v6 (list of IPv6), flags (set)."""
    relays, cur = [], None
    for line in text.splitlines():
        if line.startswith("r "):
            p = line.split()
            cur = {"ip": p[6], "v6": [], "flags": set()}
            relays.append(cur)
        elif cur is not None and line.startswith("a "):
            m = re.match(r"a \[([0-9a-fA-F:]+)\]:\d+", line)
            if m:
                cur["v6"].append(m.group(1))
        elif cur is not None and line.startswith("s "):
            cur["flags"] = set(line.split()[1:])
    return relays


def build(relays):
    has = lambda *fl: [r for r in relays if set(fl) <= r["flags"]]
    v4 = lambda rs: {r["ip"] for r in rs}
    v6 = lambda rs: {a for r in rs for a in r["v6"]}
    per4, per6 = Counter(r["ip"] for r in relays), Counter(a for r in relays for a in r["v6"])
    sel = lambda c, f: {k for k, n in c.items() if f(n)}
    return {
        "relays-v4": v4(relays), "relays-v6": v6(relays),
        "exits-v4": v4(has("Exit")), "exits-v6": v6(has("Exit")),
        "guards": v4(has("Guard")), "hsdir": v4(has("HSDir")),
        "guard-exit": v4(has("Guard", "Exit")), "guard-hsdir-exit": v4(has("Guard", "HSDir", "Exit")),
        "authorities-v4": v4(has("Authority")), "authorities-v6": v6(has("Authority")),
        "above1-or": sel(per4, lambda n: n > 1), "above1-or-v6": sel(per6, lambda n: n > 1),
        "2-or": sel(per4, lambda n: n == 2), "2-or-v6": sel(per6, lambda n: n == 2),
        "above2-or": sel(per4, lambda n: n > 2), "above2-or-v6": sel(per6, lambda n: n > 2),
    }


def sortkey(a):
    return (":" in a, [int(x) for x in a.split(".")] if "." in a and ":" not in a else a)


def write(lists, out, when):
    os.makedirs(out, exist_ok=True)
    head = "Updated:\n%s\n----------------------------\n" % when.strftime("%a %b %d %Y %H:%M:%S UTC")
    for name, addrs in lists.items():
        with open(os.path.join(out, name + ".txt"), "w", newline="\n") as f:
            f.write(head + "".join(a + "\n" for a in sorted(addrs, key=sortkey)))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--consensus")
    ap.add_argument("--out", default="out")
    a = ap.parse_args()
    text = open(a.consensus, encoding="utf-8", errors="replace").read() if a.consensus else fetch_latest()
    m = re.search(r"^valid-after (\S+ \S+)", text, re.M)
    when = datetime.strptime(m.group(1), "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc) if m else datetime.now(timezone.utc)
    lists = build(parse(text))
    assert len(lists["relays-v4"]) > 1000, "implausibly small consensus; refusing to write"
    write(lists, a.out, when)
    print({k: len(v) for k, v in lists.items()})
