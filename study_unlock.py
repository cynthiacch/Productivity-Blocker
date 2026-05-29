import json
import os
import hashlib
import getpass
import random
from datetime import datetime, timedelta

PENDING_FILE  = os.path.expanduser('~/.study_unlock_pending')
COOLDOWN_FILE = os.path.expanduser('~/.study_unlock_cooldown')

#  Decryption  (must match study_lock.py)

def decrypt(data: dict, password: str) -> str:
    salt = bytes.fromhex(data['salt'])
    ct   = bytes.fromhex(data['ct'])
    key  = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 200_000, dklen=len(ct))
    return bytes(a ^ b for a, b in zip(ct, key)).decode()

#  Delay helpers

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
    until = datetime.now() + timedelta(hours=3)
    with open(COOLDOWN_FILE, 'w') as f:
        json.dump({'cooldown_until': until.timestamp()}, f)

def _load_cooldown():
    if not os.path.exists(COOLDOWN_FILE):
        return None
    with open(COOLDOWN_FILE) as f:
        return datetime.fromtimestamp(json.load(f)['cooldown_until'])

#  Main

print("=" * 45)
print("       🔓  STUDY SESSION UNLOCK")
print("=" * 45)

# find locked devices
locked = [d for d in ("mac", "ipad", "iphone")
          if os.path.exists(os.path.expanduser(f'~/.study_lock_{d}'))]

if not locked:
    print("\n  ❌ No devices are currently locked.")
    print("     Run study_lock.py first!\n")
    exit()

print(f"\n  🔒 Currently locked: {', '.join(d.capitalize() for d in locked)}")
print("\n  Which device do you want to unlock?")
for i, d in enumerate(locked, 1):
    print(f"    {i}. {d.capitalize()}")
print(f"    {len(locked)+1}. All devices")

choice = input("\n→ Enter number: ").strip()
try:
    choice_num = int(choice)
except ValueError:
    print("❌ Invalid choice.")
    exit()

if choice_num == len(locked) + 1:
    selected = locked
elif 1 <= choice_num <= len(locked):
    selected = [locked[choice_num - 1]]
else:
    print("❌ Invalid choice.")
    exit()

# confirm
print(f"\n  ⚠️  Unlock {', '.join(d.capitalize() for d in selected)}?")
confirm = input("  Reveal PIN(s)? (y/n): ").strip().lower()
if confirm != 'y':
    print("\n  ✅ Good choice! Keep studying 💪\n")
    exit()

# check cooldown
now      = datetime.now()
cooldown = _load_cooldown()
if cooldown and now < cooldown:
    remaining = cooldown - now
    hrs  = int(remaining.total_seconds() // 3600)
    mins = int((remaining.total_seconds() % 3600) // 60)
    print()
    print(f"  🚫 You cancelled a request recently.")
    print(f"     You can't request again for another {hrs}h {mins}m.")
    print(f"     (Cooldown ends at {cooldown.strftime('%I:%M %p')})\n")
    exit()

# check / set delay
pending = _load_pending()

if pending is None:
    delay_mins  = random.randint(30, 420)
    unlock_time = now + timedelta(minutes=delay_mins)
    _save_pending(unlock_time)

    hrs  = delay_mins // 60
    mins = delay_mins % 60
    wait_str = f"{hrs}h {mins}m" if hrs > 0 else f"{mins}m"

    print()
    print(f"  ⏳ Unlock request recorded.")
    print(f"     Come back at  {unlock_time.strftime('%I:%M %p')}  and run this again.")
    print(f"     (That's {wait_str} from now — exact time is random.)")
    print()
    print("  💡 If the urge has passed by then, great!")
    print("  ❌ To cancel:  delete ~/.study_unlock_pending\n")
    exit()

elif now < pending:
    remaining = pending - now
    mins = int(remaining.total_seconds() // 60)
    secs = int(remaining.total_seconds() % 60)
    print()
    print(f"  🚫 Not yet! Come back in  {mins}m {secs}s")
    print(f"     (Unlocks at {pending.strftime('%I:%M %p')})\n")
    exit()

# delay passed → ask for password
_clear_pending()
print()
pw = getpass.getpass("  🔐 Enter session password: ")
print()

# decrypt & display
failed = False
for device in selected:
    path = os.path.expanduser(f'~/.study_lock_{device}')
    with open(path) as f:
        data = json.load(f)
    try:
        pin = decrypt(data, pw)
        print(f"  🔑 {device.capitalize()} Screen Time PIN:  👉  {pin}  👈")
        os.remove(path)
    except Exception:
        print(f"  ❌ Wrong password — could not decrypt {device.capitalize()} PIN.")
        failed = True

print()
if not failed:
    print("  ✅ Lock(s) removed. Enter the PIN in Screen Time settings.")
else:
    print("  ⚠️  Some PINs could not be decrypted (wrong password?).")
    print("     The lock files were NOT deleted — try again.")
    _save_cooldown()
print("=" * 45)
