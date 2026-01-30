
import os
import sys

# Standard macOS paths
RESOLVE_SCRIPT_API = "/Library/Application Support/Blackmagic Design/DaVinci Resolve/Developer/Scripting"
RESOLVE_SCRIPT_LIB = "/Applications/DaVinci Resolve/DaVinci Resolve.app/Contents/Libraries/Fusion/fusionscript.so"
MODULES_PATH = os.path.join(RESOLVE_SCRIPT_API, "Modules")

print(f"Setting environment...")
os.environ["RESOLVE_SCRIPT_API"] = RESOLVE_SCRIPT_API
os.environ["RESOLVE_SCRIPT_LIB"] = RESOLVE_SCRIPT_LIB

print(f"Adding to sys.path: {MODULES_PATH}")
sys.path.append(MODULES_PATH)

print("Importing DaVinciResolveScript...")
try:
    import DaVinciResolveScript as dvr_script
    print("Import successful.")
except ImportError as e:
    print(f"Import failed: {e}")
    sys.exit(1)

print("Attempting to connect to Resolve...")
try:
    resolve = dvr_script.scriptapp("Resolve")
    if resolve:
        print(f"SUCCESS! Connected to {resolve.GetProductName()} {resolve.GetVersionString()}")
    else:
        print("FAILURE: scriptapp('Resolve') returned None.")
        print("Possible causes:")
        print("1. DaVinci Resolve is not running.")
        print("2. External Scripting is disabled in Preferences.")
        print("3. You are using the Free version (sometimes has issues).")
except Exception as e:
    print(f"Error during connection: {e}")
