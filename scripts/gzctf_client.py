#!/usr/bin/env python3
"""Minimal GZCTF API client for a single game.

The API surface here follows the public GZCTF project's conventions
(https://github.com/GZTimeWalker/GZCTF). It has NOT been verified against
your specific instance -- this environment cannot reach non-443 HTTPS ports,
so the client was written from known GZCTF behavior rather than tested live.
If an endpoint 404s, run the CLI with -v and check the raw response; GZCTF
versions occasionally rename routes.

Run everything through environment variables so the token never ends up in
git history:

    export GZCTF_BASE_URL="https://43.139.207.111:9443"
    export GZCTF_TOKEN="<value of the GZCTF_Token cookie only, no 'GZCTF_Token=' prefix>"
    export GZCTF_GAME_ID=35

    python3 scripts/gzctf_client.py challenges
    python3 scripts/gzctf_client.py challenge <challengeId>
    python3 scripts/gzctf_client.py start <challengeId>
    python3 scripts/gzctf_client.py stop <challengeId>
    python3 scripts/gzctf_client.py submit <challengeId> 'flag{...}'
    python3 scripts/gzctf_client.py status <challengeId> <submitId>
"""
import argparse
import json
import os
import sys
import time

import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BASE_URL = os.environ.get("GZCTF_BASE_URL", "").rstrip("/")
TOKEN = os.environ.get("GZCTF_TOKEN", "")
GAME_ID = os.environ.get("GZCTF_GAME_ID", "")
INSECURE = os.environ.get("GZCTF_INSECURE", "1") != "0"  # most GZCTF boxes use self-signed certs


def session():
    if not BASE_URL or not TOKEN:
        sys.exit("Set GZCTF_BASE_URL and GZCTF_TOKEN environment variables first.")
    s = requests.Session()
    s.cookies.set("GZCTF_Token", TOKEN)
    s.verify = not INSECURE
    s.headers["User-Agent"] = "gzctf-client/1.0"
    return s


def game_id(explicit=None):
    gid = explicit or GAME_ID
    if not gid:
        sys.exit("Set GZCTF_GAME_ID or pass --game.")
    return gid


def pretty(resp):
    try:
        return json.dumps(resp.json(), ensure_ascii=False, indent=2)
    except ValueError:
        return resp.text


def cmd_challenges(s, args):
    r = s.get(f"{BASE_URL}/api/game/{game_id(args.game)}/details")
    print(f"HTTP {r.status_code}")
    print(pretty(r))


def cmd_challenge(s, args):
    r = s.get(f"{BASE_URL}/api/game/{game_id(args.game)}/challenges/{args.challenge_id}")
    print(f"HTTP {r.status_code}")
    print(pretty(r))


def cmd_start(s, args):
    r = s.post(f"{BASE_URL}/api/game/{game_id(args.game)}/container/{args.challenge_id}")
    print(f"HTTP {r.status_code}")
    print(pretty(r))


def cmd_stop(s, args):
    r = s.delete(f"{BASE_URL}/api/game/{game_id(args.game)}/container/{args.challenge_id}")
    print(f"HTTP {r.status_code}")
    print(pretty(r))


def cmd_submit(s, args):
    r = s.post(
        f"{BASE_URL}/api/game/{game_id(args.game)}/challenges/{args.challenge_id}",
        json={"flag": args.flag},
    )
    print(f"HTTP {r.status_code}")
    print(pretty(r))
    if r.ok:
        try:
            submit_id = r.json()
            print(f"\nsubmitId: {submit_id}")
            print("Poll it with: status", args.challenge_id, submit_id)
        except ValueError:
            pass


def cmd_status(s, args):
    r = s.get(
        f"{BASE_URL}/api/game/{game_id(args.game)}/challenges/{args.challenge_id}/status/{args.submit_id}"
    )
    print(f"HTTP {r.status_code}")
    print(pretty(r))


def cmd_watch(s, args):
    """Submit a flag and poll until GZCTF resolves it (Accepted / WrongAnswer)."""
    r = s.post(
        f"{BASE_URL}/api/game/{game_id(args.game)}/challenges/{args.challenge_id}",
        json={"flag": args.flag},
    )
    if not r.ok:
        print(f"submit failed: HTTP {r.status_code}\n{pretty(r)}")
        return
    submit_id = r.json()
    print(f"submitted, id={submit_id}, polling...")
    for _ in range(30):
        time.sleep(2)
        sr = s.get(
            f"{BASE_URL}/api/game/{game_id(args.game)}/challenges/{args.challenge_id}/status/{submit_id}"
        )
        result = sr.text.strip().strip('"')
        print(f"  -> {result}")
        if result and result not in ("FlagSubmitted", ""):
            return
    print("gave up waiting for a final verdict, check manually with `status`")


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--game", help="override GZCTF_GAME_ID")
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("challenges").set_defaults(func=cmd_challenges)

    sp = sub.add_parser("challenge")
    sp.add_argument("challenge_id")
    sp.set_defaults(func=cmd_challenge)

    sp = sub.add_parser("start")
    sp.add_argument("challenge_id")
    sp.set_defaults(func=cmd_start)

    sp = sub.add_parser("stop")
    sp.add_argument("challenge_id")
    sp.set_defaults(func=cmd_stop)

    sp = sub.add_parser("submit")
    sp.add_argument("challenge_id")
    sp.add_argument("flag")
    sp.set_defaults(func=cmd_submit)

    sp = sub.add_parser("status")
    sp.add_argument("challenge_id")
    sp.add_argument("submit_id")
    sp.set_defaults(func=cmd_status)

    sp = sub.add_parser("watch", help="submit + poll until resolved")
    sp.add_argument("challenge_id")
    sp.add_argument("flag")
    sp.set_defaults(func=cmd_watch)

    args = p.parse_args()
    s = session()
    args.func(s, args)


if __name__ == "__main__":
    main()
