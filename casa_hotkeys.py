import time
import keyboard
import switch_casa
from switch_casa import TARGET_PIDS, switch_device_host

def switch_all(host_number):
    print(f"HotKey Detected: Switching to Host {host_number}...")
    for pid in TARGET_PIDS:
        try:
            switch_device_host(pid, host_number)
        except Exception as e:
            print(f"Error switching {pid}: {e}")

def main():
    print("Casa Switcher Service Started.")
    print("Press Ctrl+Alt+Left for Host 1")
    print("Press Ctrl+Alt+Right for Host 2")
    
    # Register Hotkeys
    keyboard.add_hotkey('ctrl+alt+left', lambda: switch_all(1))
    keyboard.add_hotkey('ctrl+alt+right', lambda: switch_all(2))
    
    # Keep the script running
    keyboard.wait()

if __name__ == "__main__":
    main()
