import subprocess
import sys
import os
import json
import re
import random
from datetime import datetime, timedelta

HOSTS_FILE    = '/etc/hosts'
MARKER_START  = '# === STUDY BLOCKER START ==='
MARKER_END    = '# === STUDY BLOCKER END ==='
PENDING_FILE  = os.path.expanduser('~/.study_blocker_pending_stop')
COOLDOWN_FILE = os.path.expanduser('~/.study_blocker_cooldown')

BLOCKED_SITES = [
    'instagram.com',
    'facebook.com',
    'youtube.com',
    'tiktok.com',
    'reddit.com',
    'twitter.com',
    'x.com',
    'twitch.tv',
    'snapchat.com',
    'threads.net',
    'discord.com',
    'linkedin.com',
    'dcard.tw',
    'seek.com',
    'indeed.com',
    'au.indeed.com',
]

#  Hosts-file helpers

def _hosts_block():
    lines = [MARKER_START]
    for site in BLOCKED_SITES:
        lines += [f'0.0.0.0 {site}', f'0.0.0.0 www.{site}']
    lines.append(MARKER_END)
    return '\n'.join(lines)

def _is_active():
    with open(HOSTS_FILE) as f:
        return MARKER_START in f.read()

def _write_hosts(content):
    r = subprocess.run(['sudo', 'tee', HOSTS_FILE],
                       input=content.encode(), capture_output=True)
    if r.returncode != 0:
        print("\n  ❌  Could not write /etc/hosts.")
        print("     Did you cancel the password prompt?")
        sys.exit(1)
    subprocess.run(['sudo', 'dscacheutil', '-flushcache'],      capture_output=True)
    subprocess.run(['sudo', 'killall', '-HUP', 'mDNSResponder'], capture_output=True)

def _add_to_hosts():
    with open(HOSTS_FILE) as f:
        current = f.read()
    if MARKER_START in current:
        return
    _write_hosts(current.rstrip() + '\n\n' + _hosts_block() + '\n')

def _remove_from_hosts():
    with open(HOSTS_FILE) as f:
        current = f.read()
    cleaned = re.sub(
        r'\n*' + re.escape(MARKER_START) + r'.*?' + re.escape(MARKER_END) + r'\n*',
        '\n', current, flags=re.DOTALL
    )
    _write_hosts(cleaned)


#  Cleanup old proxy-based blocker (if still around)

def _cleanup_old_proxy():
    plist = os.path.expanduser('~/Library/LaunchAgents/com.studyblocker.plist')
    if os.path.exists(plist):
        subprocess.run(['launchctl', 'unload', plist], capture_output=True)
        try: os.remove(plist)
        except: pass
    try:
        services = subprocess.check_output(['networksetup', '-listallnetworkservices']).decode()
        for svc in services.split('\n')[1:]:
            svc = svc.strip()
            if not svc or svc.startswith('*'):
                continue
            subprocess.run(['networksetup', '-setwebproxystate',       svc, 'off'], capture_output=True)
            subprocess.run(['networksetup', '-setsecurewebproxystate', svc, 'off'], capture_output=True)
    except Exception:
        pass

#  Pending-stop helpers

def _save_pending(unlock_at: datetime):
    with open(PENDING_FILE, 'w') as f:
        json.dump({'unlock_at': unlock_at.timestamp()}, f)

def _load_pending():
    if not os.path.exists(PENDING_FILE):
        return None
    with open(PENDING_FILE) as f:
        return datetime.fromtimestamp(json.load(f)['unlock_at'])

def _clear_pending():
    if os.path.exists(PENDING_FILE):
        os.remove(PENDING_FILE)

def _save_cooldown():
    cooldown_until = datetime.now() + timedelta(hours=3)
    with open(COOLDOWN_FILE, 'w') as f:
        json.dump({'cooldown_until': cooldown_until.timestamp()}, f)

def _load_cooldown():
    if not os.path.exists(COOLDOWN_FILE):
        return None
    with open(COOLDOWN_FILE) as f:
        return datetime.fromtimestamp(json.load(f)['cooldown_until'])

#  Commands

def start():
    print("=" * 45)
    print("    🛡️   STARTING STUDY BLOCKER")
    print("=" * 45)

    if _is_active():
        print("\n  ⚠️  Blocker is already active!\n")
        _clear_pending()   # cancel any pending stop too
        return

    _cleanup_old_proxy()
    print("\n  📝 Adding blocked sites to /etc/hosts …")
    print("     (Your Mac will ask for your admin password)\n")
    _add_to_hosts()
    _clear_pending()

    print("  ✅ Blocker is now ACTIVE!")
    print("  🚫 Blocked:", ', '.join(BLOCKED_SITES))
    print()
    print("  ⏳ Stopping requires a random 30 min–7 hour wait.")
    print("     Run:  python3 blocker.py stop   when ready.\n")


def stop():
    print("=" * 45)
    print("    ⏳  STOP REQUEST")
    print("=" * 45)

    if not _is_active():
        print("\n  ℹ️  Blocker is not currently active.\n")
        _clear_pending()
        return

    pending = _load_pending()
    now     = datetime.now()

    if pending is None:
        # Check cooldown (triggered after a cancel) 
        cooldown = _load_cooldown()
        if cooldown and datetime.now() < cooldown:
            remaining = cooldown - datetime.now()
            hrs  = int(remaining.total_seconds() // 3600)
            mins = int((remaining.total_seconds() % 3600) // 60)
            print()
            print(f"  🚫 You cancelled a request recently.")
            print(f"     You can't request a new stop for another {hrs}h {mins}m.")
            print(f"     (Cooldown ends at {cooldown.strftime('%I:%M %p')})\n")
            return

        #  First time asking → set a random delay 
        delay_mins  = random.randint(30, 420)
        unlock_time = now + timedelta(minutes=delay_mins)
        _save_pending(unlock_time)

        hours = delay_mins // 60
        mins  = delay_mins % 60
        if hours > 0:
            wait_str = f"{hours}h {mins}m" if mins else f"{hours}h"
        else:
            wait_str = f"{mins}m"

        print()
        print(f"  ⏳ Stop request recorded.")
        print(f"     Come back at  {unlock_time.strftime('%I:%M %p')}  and run this again.")
        print(f"     (That's {wait_str} from now — exact time is random.)")
        print()
        print("  💡 If the urge has passed by then, great!")
        print("  ❌ To cancel:  python3 blocker.py cancel\n")

    elif now < pending:
        # Came back too early 
        remaining = pending - now
        mins      = int(remaining.total_seconds() // 60)
        secs      = int(remaining.total_seconds() % 60)

        print()
        print(f"  🚫 Not yet! Come back in  {mins}m {secs}s")
        print(f"     (Unlocks at {pending.strftime('%I:%M %p')})\n")

    else:
        # Delay has passed → actually unblock 
        print()
        print("  ✅ Delay passed. Removing blocks now…")
        print("     (Your Mac will ask for your admin password)\n")
        _remove_from_hosts()
        _clear_pending()
        print("  🔓 Blocker stopped. Sites are now accessible.\n")


def cancel():
    print("=" * 45)
    print("    ❌  CANCEL STOP REQUEST")
    print("=" * 45)

    if _load_pending() is None:
        print("\n  ℹ️  No pending stop request to cancel.\n")
        return

    _clear_pending()
    _save_cooldown()
    print()
    print("  ✅ Stop request cancelled. Still blocking!")
    print("  ⏳ Cooldown: you can't request a new stop for 3 hours.")
    print("  💪 Good call — keep going!\n")


def status():
    print("=" * 45)
    print("    📊  BLOCKER STATUS")
    print("=" * 45)
    active  = _is_active()
    pending = _load_pending()
    now     = datetime.now()

    print()
    if active:
        print("  🟢 ACTIVE — sites are blocked")
    else:
        print("  🔴 INACTIVE — sites are accessible")

    if pending:
        if now < pending:
            remaining = pending - now
            mins = int(remaining.total_seconds() // 60)
            secs = int(remaining.total_seconds() % 60)
            print(f"  ⏳ Stop requested — unlocks in {mins}m {secs}s")
            print(f"     (at {pending.strftime('%I:%M %p')})")
        else:
            print("  ⏳ Delay has passed — run 'stop' again to finish unblocking")

    print()
    print("  🚫 Blocked:", ', '.join(BLOCKED_SITES))
    print()


def restart():
    print("=" * 45)
    print("    🔄  RESTARTING STUDY BLOCKER")
    print("=" * 45)
    print("\n  📝 Refreshing blocked sites list…")
    print("     (Your Mac will ask for your admin password)\n")
    _remove_from_hosts()
    _add_to_hosts()
    _clear_pending()
    print("  ✅ Blocker restarted!")
    print("  🚫 Blocked:", ', '.join(BLOCKED_SITES))
    print()


#  Entry point

if __name__ == '__main__':
    cmds = {'start': start, 'stop': stop, 'cancel': cancel, 'status': status, 'restart': restart}

    if len(sys.argv) < 2 or sys.argv[1] not in cmds:
        print("Usage:")
        print("  python3 blocker.py start    → block sites")
        print("  python3 blocker.py restart  → refresh block list (no delay)")
        print("  python3 blocker.py stop     → request to unblock (random 30min–7hr wait)")
        print("  python3 blocker.py cancel   → cancel a pending stop request")
        print("  python3 blocker.py status   → check current state")
    else:
        cmds[sys.argv[1]]()
