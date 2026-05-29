import random
import json
import os
import hashlib
import time
import subprocess
import string


#  Encryption  (no external libraries needed)

def encrypt(plaintext: str, password: str) -> dict:
    salt = os.urandom(16)
    key  = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 200_000,
                                dklen=len(plaintext.encode()))
    ct   = bytes(a ^ b for a, b in zip(plaintext.encode(), key))
    return {'salt': salt.hex(), 'ct': ct.hex()}

def generate_session_password() -> str:
    """Generate a random 16-character password and copy it to clipboard."""
    chars = string.ascii_letters + string.digits
    pw = ''.join(random.choices(chars, k=16))
    subprocess.run(['pbcopy'], input=pw.encode(), check=True)
    return pw

#  Main

print("=" * 45)
print("       📚  STUDY SESSION LOCK")
print("=" * 45)

# pick devices
print("\nWhich device are you locking?")
print("  1. Mac")
print("  2. iPad")
print("  3. iPhone")
print("  4. All devices")
choice = input("\n→ Enter number: ").strip()

DEVICE_MAP = {"1": ["mac"], "2": ["ipad"], "3": ["iphone"], "4": ["mac", "ipad", "iphone"]}
if choice not in DEVICE_MAP:
    print("❌ Invalid choice.")
    exit()

selected = DEVICE_MAP[choice]

# generate session password 
print()
print("  🔐 Generating a random session password…")
pw = generate_session_password()

print()
print("  ┌─────────────────────────────────────┐")
print(f"  │  Session password:  {pw}  │")
print("  │  ✅ Already copied to your clipboard │")
print("  └─────────────────────────────────────┘")
print()
print("  ⚠️  Paste it somewhere safe RIGHT NOW")
print("     (Notes app, another device, etc.)")
print("     It disappears in 10 seconds!\n")

for t in range(10, 0, -1):
    print(f"   Hiding in {t}…", end='\r')
    time.sleep(1)

subprocess.run(['clear'])
print("=" * 45)
print("  🔒 Session password hidden!")
print("     Make sure you saved it somewhere.\n")

input("  Press Enter to continue locking… ")

# generate & save PINs 
pins = {}
for device in selected:
    save_path = os.path.expanduser(f'~/.study_lock_{device}')
    if os.path.exists(save_path):
        print(f"\n  ⚠️  {device.capitalize()} is already locked!")
        confirm = input(f"     Replace with a new PIN? (y/n): ").strip().lower()
        if confirm != 'y':
            print(f"  ⏭  Skipping {device.capitalize()}…")
            continue

    pin = str(random.randint(1000, 9999))
    pins[device] = pin
    encrypted = encrypt(pin, pw)
    with open(save_path, 'w') as f:
        json.dump(encrypted, f)
    os.chmod(save_path, 0o600)

if not pins:
    print("\n❌ No devices were locked.")
    exit()

# reveal PINs for 5 seconds each 
print()
print("  ⚠️  PINs appear for 5 seconds each.")
print("     Open Screen Time on each device first!")
input("\n  Ready? Press Enter to reveal PINs… ")

for i, (device, pin) in enumerate(pins.items()):
    print("\n" + "=" * 45)
    print(f"   🔑  {device.upper()} SCREEN TIME PIN:  {pin}")
    print("=" * 45)
    for t in range(5, 0, -1):
        print(f"   Hiding in {t}…", end='\r')
        time.sleep(1)
    subprocess.run(['clear'])
    print(f"  ✅ {device.capitalize()} PIN hidden!")
    if i < len(pins) - 1:
        input("  Press Enter when ready for next device… ")

subprocess.run(['clear'])
print("=" * 45)
print("       📚  STUDY SESSION LOCK")
print("=" * 45)
print(f"\n  ✅ Locked: {', '.join(d.capitalize() for d in pins)}")
print("  🔒 PINs encrypted — only unlockable with")
print("     your saved session password.")
print()
print("  To reveal a PIN later:")
print("  python3 ~/Downloads/block/study_unlock.py")
print()
print("  💪 Good luck studying! You got this!")
print("=" * 45)
