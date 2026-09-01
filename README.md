# CTF toolkit (GZCTF game 35)

This session's sandbox cannot reach `43.139.207.111:9443` directly: the
network policy here explicitly blocks non-443 HTTPS ports (see
`/root/.ccr/README.md`'s "not supported through the proxy" section), so
these scripts are written for you to run **locally**, on a machine that can
actually reach the CTF host.

## Setup

```bash
pip install -r scripts/requirements.txt

export GZCTF_BASE_URL="https://43.139.207.111:9443"
export GZCTF_TOKEN="<the value of the GZCTF_Token cookie, without the 'GZCTF_Token=' prefix>"
export GZCTF_GAME_ID=35
```

Don't commit real tokens to this repo -- they go in your shell environment
only. `.gitignore` already excludes `.env`.

## 1. List challenges / check status

```bash
python3 scripts/gzctf_client.py challenges
python3 scripts/gzctf_client.py challenge <challengeId>
```

The API paths follow public GZCTF conventions but haven't been verified
against this specific instance (couldn't reach it from here). If a call
404s, open the challenge in a browser, check devtools' Network tab for the
real path, and tell me -- I'll patch `gzctf_client.py`.

## 2. Start a challenge instance

```bash
python3 scripts/gzctf_client.py start <challengeId>
```

This returns the instance's exposed URL/port (container entry).

## 3. Attack it

For the "Ping!" command-injection series, point `ping_bypass.py` at the
instance:

```bash
python3 scripts/ping_bypass.py \
  --url http://<instance-ip>:<port>/ \
  --param ip \
  --cmd "cat /flag* 2>/dev/null; cat flag* 2>/dev/null"
```

It runs through common filter-bypass techniques (`;`, `|`, `&&`, backticks,
`$()`, raw newline, CRLF, `$IFS` for blocked spaces, ...) one at a time and
stops as soon as a `flag{...}` pattern shows up in the response. Use
`--list` to just print the payload set without sending anything, useful for
hand-tuning against a specific level's filter.

For other challenge types (the "神秘验证码生成器" one, etc.) there's no
generic script -- inspect it manually, then either write a small one-off
script under `scripts/` or just solve it by hand.

## 4. Submit the flag

```bash
python3 scripts/gzctf_client.py watch <challengeId> 'flag{...}'
```

`watch` submits and polls until GZCTF returns a final verdict
(Accepted/WrongAnswer). Use plain `submit` + `status` if you want to check
manually.

## 5. Report back

Paste me the flag (and which challenge it was for), or the raw
request/response if a script needs adjusting. I'll:
- update `writeups/PROGRESS.md`,
- write a proper `writeups/<challenge-name>.md` from the template,
- commit and push to this branch.

I won't fabricate flags or progress -- only what you actually confirm as
solved goes in.
