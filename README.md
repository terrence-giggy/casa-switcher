# Logitech Casa Switcher

A simple Python utility to programmatically switch the Bluetooth host of your **Logitech Casa** keyboard and touchpad (and likely other modern Logitech MX devices).

## Why?
Logi Options+ is great, but sometimes you just want a simple, reliable way to switch your keyboard and mouse between two computers without the bloat or lag. This tool uses the **HID++ 2.0** protocol to send direct commands to the devices.

## Features
- **Instant Switching**: Switch both keyboard and touchpad with a single hotkey.
- **Directional Hotkeys**: Defaults to `Ctrl + Alt + Left` (Host 1) and `Ctrl + Alt + Right` (Host 2).
- **Silent Service**: Runs in the background with no popups.
- **Generic Support**: Designed for Logitech Casa but works with other HID++ compliant devices (MX Keys, MX Master) if you update the PIDs.

## Installation & Setup

1.  **Install Python**: Make sure Python is installed on your machine.
2.  **Clone this repo**:
    ```bash
    git clone https://github.com/your-username/casa-switcher.git
    cd casa-switcher
    ```
3.  **Run `install.bat`**:
    Double-click `install.bat`. This script will automatically:
    *   Install Python dependencies.
    *   Create a default `config.json` if it doesn't exist.
    *   Create a shortcut in your Startup folder so the service runs on login.

4.  **Start the Service**:
    You can simply restart your computer, or run `start_casa_service.bat` to start it immediately.

## Configuration

*   **Edit `config.json`**:
    Modify this file to change the host ID (`1` or `2`), the `trigger_corner` (for mouse switching), or the `safe_corner`.

*   **Device IDs (Optional)**:
    The script is pre-configured for the standard Casa Keyboard (`0xB371`) and Touchpad (`0xBB00`). To use other devices, run `python scan_casa.py` to find their IDs, then update `TARGET_PIDS` in `switch_casa.py`.

## Usage

*   **Ctrl + Alt + Left Arrow**: Switch to Bluetooth Slot 1
*   **Ctrl + Alt + Right Arrow**: Switch to Bluetooth Slot 2

## Logging & Troubleshooting

The service automatically logs any errors or exceptions to a file named `casa_switcher_errors.log` located in the same directory as the script.
*   **Log Behavior**: The log file is **cleared every time the service starts**, so it only contains errors from the current session.
*   **What is logged**: Only errors and critical failures (e.g., config loading issues, HID communication errors).

## Files

*   `switch_casa.py`: Key logic for sending HID++ commands. Can be used as a CLI tool (`python switch_casa.py 1`).
*   `casa_hotkeys.py`: Background service that listens for keyboard shortcuts.
*   `scan_casa.py`: Utility to find attached Logitech devices and their PIDs.
*   `requirements.txt`: Python dependencies.
