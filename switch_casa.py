import hid
import sys
import time

# --- Configuration ---
# Logitech Vendor ID
VENDOR_ID = 0x046D

# Casa Device PIDs
# 0xB371 = Casa Keyboard
# 0xBB00 = Casa Touchpad
TARGET_PIDS = [0xB371, 0xBB00]

# --- HID++ Constants ---
# 0x1814 is the "Change Host" feature in HID++ 2.0
FEATURE_HOSTS_INFO = 0x1814
CMD_SWITCH_HOST = 0x10 

def find_hidpp_interface(pid):
    """
    Finds the specific interface that speaks HID++.
    Iterates through all interfaces for the PID, sends a ping, 
    and returns the open handle for the first one that replies.
    """
    interfaces = hid.enumerate(VENDOR_ID, pid)
    if not interfaces:
        return None

    # Sort: Try 0xFF43 (Logitech HID++) first, then others
    # 0xFF43 is the standard Logitech HID++ page
    interfaces.sort(key=lambda x: x['usage_page'] == 0xFF43, reverse=True)

    for interface in interfaces:
        path = interface['path']
        # Filter out obvious non-candidates to save time/errors
        # Keyboard/Consumer pages usually don't support raw HID++ commands 
        # unless they are the *only* interfaces.
        # But we will try them if 0xFF43 fails.
        
        try:
            h = hid.device()
            h.open_path(path)
            
            # Ping Method 1: Short Packet (0x10) - Root GetFeature(0x0001)
            # Some devices only answer to 0x10, some to 0x11.
            # We try 0x11 first as it's safer for modern devices.
            
            # Ping: Report 0x11, Dev 0xFF, Feat 0x00, Func 0x01 (GetFeature), Param: 0x0001 (Feature Set)
            # Asking: "What index is the Feature Set feature?"
            # This is a safe read-only query.
            # Using 0x00, 0x00 (Root) might be safer? Let's use Root(0x0000).
            
            # CMD: GetFeature(FeatureSet 0x0001)
            cmd = [0x11, 0xFF, 0x00, 0x00, 0x00, 0x01] + [0x00] * 14
            
            h.write(cmd)
            res = h.read(20, 500) # Short timeout
            
            if res:
                # Valid response! This is our interface.
                # Flush any other pending reads
                try: 
                    while h.read(20, 10): pass 
                except: pass
                
                print(f"  [+] Found HID++ Interface at {path} (Usage Page 0x{interface['usage_page']:X})")
                return h
            
            h.close()
        except Exception:
            continue
            
    return None

def hidpp_request(dev, feature_index, function_id, params=None):
    """
    Sends a formatted HID++ 2.0 request.
    Packet: [ReportID (0x11), DeviceIdx (0xFF), FeatureIdx, FunctionID, Params..., Padding]
    """
    if params is None: 
        params = []
    
    report_id = 0x11  # Long message
    device_index = 0xFF # The device itself
    
    cmd = [report_id, device_index, feature_index, function_id] + params
    # Pad to 20 bytes
    cmd += [0x00] * (20 - len(cmd))
    
    try:
        dev.write(cmd)
        # Read response (timeout 1s) with buffer 20 bytes
        response = dev.read(20, 1000)
        return response
    except Exception as e:
        print(f"  Communication Error: {e}")
        return None

def get_feature_index(dev, feature_id):
    """
    Queries the 'Root' feature (Index 0) to find the runtime index of a feature.
    """
    # Root Feature Index = 0x00
    # Function 0x00 = GetFeature(FeatureID)
    feat_id_high = (feature_id >> 8) & 0xFF
    feat_id_low  = feature_id & 0xFF
    
    # Send request to Root
    response = hidpp_request(dev, 0x00, 0x00, [feat_id_high, feat_id_low])
    
    if response and len(response) > 4:
        # Byte 4 is the feature index
        return response[4]
    return None

def switch_device_host(pid, host_number):
    """
    Connects to device by PID and tells it to switch to host_number (1, 2, or 3).
    """
    dev = find_hidpp_interface(pid)
    if not dev:
        print(f"[-] Device (PID {pid:04X}) not found or refused HID++ connection.")
        return

    try:
        # 1. Find the index for the 'Change Host' feature
        host_feature_idx = get_feature_index(dev, FEATURE_HOSTS_INFO)
        
        if not host_feature_idx:
            print(f"[-] Device (PID {pid:04X}) does not support Host Switching (Feature 0x1814).")
            return

        # 2. Send the switch command
        # Host index 0 = Slot 1, 1 = Slot 2...
        target_idx = host_number - 1
        print(f"[+] Device (PID {pid:04X}): Switching to Host {host_number}...")
        
        hidpp_request(dev, host_feature_idx, CMD_SWITCH_HOST, [target_idx])
        
    finally:
        dev.close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python switch_casa.py <host_number: 1, 2, or 3>")
        sys.exit(1)
        
    try:
        target_host = int(sys.argv[1])
        if target_host not in [1, 2, 3]:
            raise ValueError
    except ValueError:
        print("Error: Host number must be 1, 2, or 3.")
        sys.exit(1)

    print(f"Attempting to switch all Casa devices to Host {target_host}...")
    
    for pid in TARGET_PIDS:
        switch_device_host(pid, target_host)

    print("Done.")
