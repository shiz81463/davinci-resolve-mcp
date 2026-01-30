import asyncio
import os
import sys

# Add the project root to sys.path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, project_root)

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# System files to ignore
IGNORE_FILES = {'.DS_Store', 'Thumbs.db'}

async def run():
    # Setup server parameters
    server_script = os.path.join(project_root, "src", "resolve_mcp_server.py")
    python_exe = sys.executable
    
    # Set PYTHONPATH
    env = os.environ.copy()
    env["PYTHONPATH"] = project_root + os.pathsep + env.get("PYTHONPATH", "")

    server_params = StdioServerParameters(
        command=python_exe,
        args=[server_script],
        env=env
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            # 1. Open Project
            print("Opening project 'imax countdown'...")
            try:
                result = await session.call_tool("open_project", arguments={"name": "imax countdown"})
                print(result.content[0].text)
            except Exception as e:
                print(f"Error opening project: {e}")
                return

            source_dir = "/Users/ziconghuang/Downloads/IMAX_Countdown"
            print(f"Scanning {source_dir}...")
            
            # Walk the directory
            for root, dirs, files in os.walk(source_dir):
                # Calculate relative path for bin structure
                rel_path = os.path.relpath(root, source_dir)
                
                if rel_path == ".":
                    bin_path = "Master"
                else:
                    # Resolve uses forward slashes
                    bin_path = rel_path.replace(os.path.sep, "/")
                
                # Check if there are valid files to import
                valid_files = [f for f in files if f not in IGNORE_FILES and not f.startswith('.')]
                
                if not valid_files and rel_path != ".":
                    # Even if no files, we might want to create the bin structure?
                    # Let's create it anyway if it's not root
                    pass

                # Create Bin Structure if not Master
                if bin_path != "Master":
                    print(f"\nEnsuring bin path: {bin_path}")
                    try:
                        await session.call_tool("create_bin_path", arguments={"path": bin_path})
                    except Exception as e:
                        print(f"  Error creating bin: {e}")
                        continue

                # Set Current Bin
                print(f"Setting target bin: {bin_path}")
                try:
                    await session.call_tool("set_media_pool_current_folder", arguments={"path": bin_path})
                except Exception as e:
                    print(f"  Error setting bin: {e}")
                    continue
                
                # Import Files
                for file in valid_files:
                    full_path = os.path.join(root, file)
                    print(f"  Importing: {file}")
                    try:
                        # ImportMedia imports to current bin
                        result = await session.call_tool("import_media", arguments={"file_path": full_path})
                        print(f"    Result: {result.content[0].text}")
                    except Exception as e:
                        print(f"    Failed: {e}")

            print("\nImport complete.")

if __name__ == "__main__":
    asyncio.run(run())
