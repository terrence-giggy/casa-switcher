import hid
import sys

# Logitech Casa Device IDs
# Default PID for Casa Keyboard: 0xB371 (User provided)
# Default PID for Casa Touchpad: 0xBB00 (User provided)
devices_to_scan = [0xB371, 0xBB00] 
VENDOR_ID = 0x046D

print("Scanning Logitech Devices...")

try:
    # Check if hid module works
    hid.enumerate(VENDOR_ID, 0)
except Exception as e:
    print(f"CRITICAL ERROR: Could not enumerate devices. {e}")
    sys.exit(1)

for pid in devices_to_scan:
    print(f"\n--- Checking Device PID: {pid:04X} ---")
    try:
        # Enumerate interfaces
        interfaces = hid.enumerate(VENDOR_ID, pid)
        if not interfaces:
            print("  Device not found (check USB/Bluetooth connection)")
            # Try to list all logitech devices to see if we have the wrong PID
            all_logi = hid.enumerate(VENDOR_ID, 0)
            if all_logi:
                print("  Found other Logitech devices:")
                for d in all_logi:
                    # Avoid printing dupes
                    seen = set()
                    for d in all_logi:
                        if d['product_id'] not in seen:
                            print(f"    - PID: {d['product_id']:04X} | {d['product_string']}")
                            seen.add(d['product_id'])
            continue

        target_path = None
        # Priority: Usage Page 0xFF00 (Vendor Specific) for HID++
        for i in interfaces:
            if i['usage_page'] == 0xFF00:
                target_path = i['path']
                break
        
        # Fallback: try the first interface
        if not target_path and interfaces:
            target_path = interfaces[0]['path']
        
        if not target_path:
            print("  No suitable HID++ interface found.")
            continue

        # print(f"  Opening device at path: {target_path}")
        h = hid.device()
        h.open_path(target_path)
        print(f"  Successfully opened device! (No 'Options+' Lock conflict)")

        # Candidates for Host Switching Feature
        # 0x1814 (ChangeHost - older/unifying)
        # 0x4500 (HostSwitching - Bolt/Newer)
        # 0x0001 (IFeatureSet - Root)
        
        candidates = [0x1814, 0x4500, 0x0001]
        
        found_any = False
        for feat_id in candidates:
            # Cmd: 10 <dev> <feat_idx> <func> ...
            # We use Root(00) Feature(00) Func(00) = GetFeatureIndex(feat_id)
            # Packet: 10 FF 00 00 <ID_High> <ID_Low> 00
            
            feat_high = (feat_id >> 8) & 0xFF
            feat_low = feat_id & 0xFF
            
            cmd = [0x10, 0xFF, 0x00, feat_high, feat_low, 0x00, 0x00]
            try:
                h.write(bytes(cmd))
                
                # Read response
                res = h.read(20, timeout_ms=500)
                if res:
                    # Valid response for GetFeatureIndex: 11 FF 00 <Index> <Type> <Ver> ...
                    if res[0] in [0x10, 0x11] and res[1] == 0xFF:
                        feat_index = res[4]
                        if feat_index != 0:
                            print(f"  [FOUND] Feature {feat_id:04X} is at Index {feat_index:02X}")
                            found_any = True
                        else:
                            pass # print(f"  [MISS] Feature {feat_id:04X} not supported.")
                else:
                    pass # print(f"  [TIMEOUT] No response for {feat_id:04X}")
            except Exception as ex:
                print(f"  [ERROR] Writing to device failed: {ex}")

        if not found_any:
            print("  [WARNING] Opened device but found no known Host Switching features.")

        h.close()

    except OSError as e:
        print(f"  [LOCKED] Cannot open device: {e}")
        print("  -> Logi Options+ is likely running and holding an exclusive lock.")
        print("  -> Please CLOSE Logi Options+ via Task Manager and try again.")
    except Exception as e:
        print(f"  [ERROR] {e}")

print("\nScan complete.")