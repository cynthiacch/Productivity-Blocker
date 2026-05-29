# Self-Discipline Productivity Blocker

I have been addicted to social media since I was a kid, so I built this tool to help myself focus.

A macOS productivity tool that blocks distracting websites at the OS level and locks Screen Time PINs with cryptographic encryption — designed to make impulsive social media access genuinely difficult.

---

## How It Works

Blocking works by editing `/etc/hosts` to redirect distracting sites to `0.0.0.0` (nowhere). This operates **below the browser level** — it affects Safari, Chrome, Firefox, every app, and every network. No proxy, no extension, no workaround.

---

## Files

| File | Purpose |
|---|---|
| `blocker.py` | Blocks/unblocks social media sites. Stopping requires a **random 30min–7hr delay** to deter impulsive unblocking. |
| `study_lock.py` | Generates an encrypted Screen Time PIN for iPhone/iPad/Mac. Auto-generates a session password copied to clipboard. The password will onyl show up for five seconds so it will be hard to remember it. |
| `study_unlock.py` | Reveals the Screen Time PIN after a **random 30min–7hr delay** + correct session password. |


---

## Blocked Sites

`instagram.com` `facebook.com` `youtube.com` `tiktok.com` `reddit.com` `twitter.com` `x.com` `twitch.tv` `snapchat.com` `threads.net` `discord.com` `linkedin.com` `dcard.tw` `seek.com` `indeed.com`

---

## Setup

```bash
# 1. Start the website blocker
python3 blocker.py start

# 2. Set up job site blocking (run once)
python3 job_access.py setup
