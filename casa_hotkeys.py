import time
import keyboard
import mouse
import ctypes
import json
import os
import switch_casa
from switch_casa import TARGET_PIDS, switch_device_host

# --- Config ---
CONFIG_FILE = "config.json"
DEFAULT_CONFIG = {
    "this_host_id": 1,
    "trigger_corner": "top-right", # top-right, top-left, bottom-right, bottom-left
    "safe_corner": "top-left"
}

def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading config: {e}")
    return DEFAULT_CONFIG

config = load_config()
THIS_HOST = config.get("this_host_id", 1)
TRIGGER_CORNER = config.get("trigger_corner", "top-right")
SAFE_CORNER = config.get("safe_corner", "top-left")

print(f"Loaded Config: Host {THIS_HOST}, Trigger: {TRIGGER_CORNER}, Safe: {SAFE_CORNER}")

# Track current host state (We initialize to "this" host because we are running on it)
# When we switch away, this value changes.
current_host = THIS_HOST

def switch_all(host_number):
    global current_host
    current_host = host_number
    print(f"HotKey Detected: Switching to Host {host_number}...")
    
    # 1. Force-release the modifier keys intentionally.
    # If the keyboard disconnects while these are 'down', Windows thinks they are stuck.
    # We send synthetic 'Key Up' events to the OS before cutting the connection.
    try:
        keyboard.release('ctrl')
        keyboard.release('alt')
        keyboard.release('left')
        keyboard.release('right')
    except Exception:
        pass

    # 2. Add a short delay to allow the OS to register the 'Key Up' events.
    time.sleep(0.3)

    for i, pid in enumerate(TARGET_PIDS):
        # Add a delay between devices (Keyboard is first, Touchpad is second)
        # This prevents signal conflict if one device switches and drops off 
        # while we are trying to talk to the second one.
        if i > 0:
            time.sleep(0.5)

        try:
            switch_device_host(pid, host_number)
        except Exception as e:
            print(f"Error switching {pid}: {e}")

def get_screen_size():
    """Returns (width, height) of the primary screen."""
    user32 = ctypes.windll.user32
    return user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)

def is_in_corner(x, y, width, height, corner_name):
    margin = 5
    if corner_name == "top-right":
        return x >= width - margin and y <= margin
    elif corner_name == "top-left":
        return x <= margin and y <= margin
    elif corner_name == "bottom-right":
        return x >= width - margin and y >= height - margin
    elif corner_name == "bottom-left":
        return x <= margin and y >= height - margin
    return False

def move_to_safe_corner(width, height, corner_name):
    if corner_name == "top-right":
        mouse.move(width, 0, absolute=True, duration=0)
    elif corner_name == "top-left":
        mouse.move(0, 0, absolute=True, duration=0)
    elif corner_name == "bottom-right":
        mouse.move(width, height, absolute=True, duration=0)
    elif corner_name == "bottom-left":
        mouse.move(0, height, absolute=True, duration=0)

def check_corner_and_switch():
    """Checks if mouse is in configured corner and switches to the OTHER host."""
    
    # Only check trigger if we believe we are currently controlling THIS host.
    # If the script thinks we are on Host 2, but we are running on Host 1,
    # technically inputs shouldn't be reaching us anyway (keyb is on Host 2).
    # But if the user manually switched back via button, our state might be out of sync.
    # However, for corner switching (Push "Away"), we usually want to push AWAY from THIS host.
    
    width, height = get_screen_size()
    
    try:
        x, y = mouse.get_position()
    except:
        return

    if is_in_corner(x, y, width, height, TRIGGER_CORNER):
        print(f"Cursor in {TRIGGER_CORNER}! Switching away from Host {THIS_HOST}...")
        
        # Target is the "other" one. (Assuming 2 hosts: 1 and 2)
        target = 2 if THIS_HOST == 1 else 1
        
        # Move Mouse Away to Safe Corner BEFORE switching to prevent loops
        move_to_safe_corner(width, height, SAFE_CORNER)
        
        # Update state and switch
        switch_all(target)
        
        # Debounce
        time.sleep(2.0)

def main():
    print("Casa Switcher Service Started.")
    print("Press Ctrl+Alt+Left for Host 1")
    print("Press Ctrl+Alt+Right for Host 2")
    print(f"Or move mouse to {TRIGGER_CORNER} to switch to Other Host.")
    
    # Register Hotkeys
    keyboard.add_hotkey('ctrl+alt+left', lambda: switch_all(1))
    keyboard.add_hotkey('ctrl+alt+right', lambda: switch_all(2))
    
    # Check for corner trigger periodically
    try:
        while True:
            check_corner_and_switch()
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("Stopping Service.")

if __name__ == "__main__":
    main()
