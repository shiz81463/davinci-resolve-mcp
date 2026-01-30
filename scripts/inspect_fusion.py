import imp
import sys

def inspect_direct():
    print("Inspecting Fusion Object...")
    # MacOS path for Resolve Scripting Library
    lib_path = "/Applications/DaVinci Resolve/DaVinci Resolve.app/Contents/Libraries/Fusion/fusionscript.so"
    
    try:
        # Load the module
        m = imp.load_dynamic("fusionscript", lib_path)
        resolve = m.scriptapp("Resolve")
        
        if not resolve:
            print("Could not connect to Resolve")
            return
            
        fusion = resolve.Fusion()
        print(f"Fusion Object: {fusion}")
        
        # List all attributes
        print("\nAttributes:")
        for attr in dir(fusion):
            print(f"  {attr}")
            
        print("\nChecking specific methods:")
        methods = ["ImportComp", "LoadComp", "OpenComp", "GetCompList"]
        for method in methods:
            if hasattr(fusion, method):
                val = getattr(fusion, method)
                print(f"  {method}: {val} (Callable: {callable(val)})")
            else:
                print(f"  {method}: Not Found")
                
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    inspect_direct()
