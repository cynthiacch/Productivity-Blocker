Self-Discipline Productivity Blocker
A macOS productivity tool that blocks distracting websites at the OS level and locks Screen Time PINs with cryptographic encryption — designed to make impulsive social media access genuinely difficult.

How It Works
Blocking works by editing /etc/hosts to redirect distracting sites to 0.0.0.0 (nowhere). This operates below the browser level — it affects Safari, Chrome, Firefox, every app, and every network. No proxy, no extension, no workaround.

Files
File	Purpose
blocker.py	Blocks/unblocks social media sites. Stopping requires a random 30min–7hr delay to deter impulsive unblocking.
study_lock.py	Generates an encrypted Screen Time PIN for iPhone/iPad/Mac. Auto-generates a session password copied to clipboard.
study_unlock.py	Reveals the Screen Time PIN after a random 30min–7hr delay + correct session password.
job_access.py	Opens seek.com and indeed.com for exactly 15 minutes, then auto-reblocks.
Blocked Sites
instagram.com facebook.com youtube.com tiktok.com reddit.com twitter.com x.com twitch.tv snapchat.com threads.net discord.com linkedin.com dcard.tw seek.com indeed.com

Setup

# 1. Start the website blocker
python3 blocker.py start

# 2. Set up job site blocking (run once)
python3 job_access.py setup
Usage
Website Blocker

python3 blocker.py start     # block all sites
python3 blocker.py stop      # request to unblock (random 30min–7hr wait)
python3 blocker.py cancel    # cancel stop request (triggers 3hr cooldown)
python3 blocker.py status    # check current state
Screen Time Lock (iPhone / iPad / Mac)

python3 study_lock.py        # generate & encrypt a Screen Time PIN
python3 study_unlock.py      # reveal PIN after random delay + session password
Job Search Mode

python3 job_access.py start  # open 15-min access window (keep terminal open!)
python3 job_access.py stop   # manually re-block early
python3 job_access.py status # check if blocked or open
Anti-Cheat Design
Attempt	Protection
Run stop immediately	Random 30min–7hr delay before it works
Cancel and re-run stop to fish for a short delay	3-hour cooldown after every cancel
Read the PIN file directly	PBKDF2-HMAC-SHA256 encryption — unreadable without session password
Edit the scripts	Folder locked with sudo chflags -R schg
Use a different browser	Hosts file blocks at OS level, not browser level
Lock / Unlock the Folder

# Lock (prevent editing)
sudo chflags -R schg ~/Downloads/block/

# Unlock (to make changes)
sudo chflags -R noschg ~/Downloads/block/
Requirements
macOS
Python 3 (pre-installed on macOS)
No external libraries needed
