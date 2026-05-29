# Self-Discipline Productivity Blocker

I have been addicted to social media since I was a kid. Even with built-in screen time limits, I found it too easy to cheat — I already knew the password, so I could just extend the limit whenever I wanted. So I built my own system with two components:

1. **A study lock** — generates random encrypted Screen Time PINs for iPhone, iPad, and Mac. The PIN is only visible for 5 seconds, making it impossible to memorise.
2. **A web blocker** — blocks distracting sites at the OS level on Mac, with a random delay before you can unblock anything.

---

## How It Works

Blocking works by editing `/etc/hosts` to redirect distracting sites to `0.0.0.0` (nowhere). This operates **below the browser level** — it affects Safari, Chrome, Firefox, every app, and every network. No proxy, no extension, no workaround.

---

## Files

| File | Purpose |
|---|---|
| `blocker.py` | Blocks/unblocks social media sites. Stopping requires a **random 30min–7hr delay** to deter impulsive unblocking. |
| `study_lock.py` | Generates an encrypted Screen Time PIN for iPhone/iPad/Mac. The session password is auto-generated, copied to clipboard, and displayed for only **10 seconds** before disappearing. |
| `study_unlock.py` | Reveals the Screen Time PIN after a **random 30min–7hr delay** + correct session password. |
| `job_access.py` | Opens seek.com and indeed.com for exactly **15 minutes**, then auto-reblocks. |

---

## Blocked Sites

`instagram.com` `facebook.com` `youtube.com` `tiktok.com` `reddit.com` `twitter.com` `x.com` `twitch.tv` `snapchat.com` `threads.net` `discord.com` `linkedin.com` `dcard.tw` `seek.com` `indeed.com`

> The blocked sites list can always be modified by editing `blocker.py`.

### Emergency / Forgot Password
If you forget your Screen Time PIN password or have a genuine emergency, you can use Apple's **"Forgot Passcode?"** option in Settings → Screen Time, sign in with your Apple ID, and reset it. You can then set a new PIN using `study_lock.py`.

---

## Setup

```bash
# 1. Start the website blocker
python3 blocker.py start

# 2. Set up job site blocking (run once)
python3 job_access.py setup
