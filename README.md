# Logitech Casa Switcher

A simple Python utility to programmatically switch the Bluetooth host of your **Logitech Casa** keyboard and touchpad (and likely other modern Logitech MX devices).

## Why?
Logi Options+ is great, but sometimes you just want a simple, reliable way to switch your keyboard and mouse between two computers without the bloat or lag. This tool uses the **HID++ 2.0** protocol to send direct commands to the devices.

## Features
- **Instant Switching**: Switch both keyboard and touchpad with a single hotkey.
- **Directional Hotkeys**: Defaults to `Ctrl + Alt + Left` (Host 1) and `Ctrl + Alt + Right` (Host 2).
- **Silent Service**: Runs in the background with no popups.
- **Generic Support**: Designed for Logitech Casa but works with other HID++ compliant devices (MX Keys, MX Master) if you update the PIDs.

## Installation

1.  **Install Python**: Make sure Python is installed on your machine.
2.  **Clone this repo**:
    ```bash
    git clone https://github.com/your-username/casa-switcher.git
    cd casa-switcher
    ```
3.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

## Setup

1.  **Find your Device IDs (Optional)**:
    The script comes pre-configured for the standard Casa Keyboard (`0xB371`) and Touchpad (`0xBB00`). If yours are different, run:
    ```bash
    python scan_casa.py
    ```
    Update `TARGET_PIDS` in `switch_casa.py` if needed.

2.  **Run the Service**:
    ```bash
    python casa_hotkeys.py
    ```

## Auto-Start on Windows

To have this run automatically when you log in:

1.  Run the included **install script** (PowerShell):
    ```powershell
    # Creates a shortcut in your Startup folder
    $StartPath = "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Startup\CasaSwitcher.lnk"
    $Target = "$PWD\start_casa_service.bat"
    $s=(New-Object -COM WScript.Shell).CreateShortcut($StartPath); $s.TargetPath=$Target; $s.Save()
    ```

    **OR**

2.  **Manually**:
    *   Press `Win + R`, type `shell:startup`, and hit Enter.
    *   Drag `start_casa_service.bat` into that folder (create a shortcut).

## Usage

*   **Ctrl + Alt + Left Arrow**: Switch to Bluetooth Slot 1
*   **Ctrl + Alt + Right Arrow**: Switch to Bluetooth Slot 2

## Files

*   `switch_casa.py`: Key logic for sending HID++ commands. Can be used as a CLI tool (`python switch_casa.py 1`).
*   `casa_hotkeys.py`: Background service that listens for keyboard shortcuts.
*   `scan_casa.py`: Utility to find attached Logitech devices and their PIDs.
*   `requirements.txt`: Python dependencies.
