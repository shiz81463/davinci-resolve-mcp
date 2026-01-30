import asyncio
import os
import sys

# Add the project root to sys.path to allow importing from src if needed
# (Though we are using the MCP client, so we don't strictly need src imports unless we use utils)
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, project_root)

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Define extensions to import
VALID_EXTENSIONS = {
    '.mov', '.mp4', '.m4v', '.avi', '.mxf', '.dv',
    '.png', '.jpg', '.jpeg', '.tiff', '.tif', '.exr', '.dpx',
    '.wav', '.mp3', '.aac', '.aiff',
    '.drp', # Project files, maybe? No, import_media is for clips.
}

async def run():
    # Setup server parameters
    server_script = os.path.join(project_root, "src", "resolve_mcp_server.py")
    python_exe = sys.executable
    
    # Set PYTHONPATH to include src
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
            
            # 1. Create Project
            print("Creating project 'imax countdown'...")
            try:
                result = await session.call_tool("create_project", arguments={"name": "imax countdown"})
                print(result.content[0].text)
            except Exception as e:
                print(f"Error creating project: {e} (It might already exist)")

            # 2. Open Project
            print("Opening project 'imax countdown'...")
            try:
                result = await session.call_tool("open_project", arguments={"name": "imax countdown"})
                print(result.content[0].text)
            except Exception as e:
                print(f"Error opening project: {e}")
                return

            # 3. Find and Import Media
            source_dir = "/Users/ziconghuang/Downloads/IMAX_Countdown"
            print(f"Scanning {source_dir}...")
            
            files_to_import = []
            for root, dirs, files in os.walk(source_dir):
                for file in files:
                    ext = os.path.splitext(file)[1].lower()
                    if ext in VALID_EXTENSIONS:
                        full_path = os.path.join(root, file)
                        files_to_import.append(full_path)
            
            print(f"Found {len(files_to_import)} media files.")
            
            # Import loop
            success_count = 0
            for file_path in files_to_import:
                print(f"Importing: {os.path.basename(file_path)}...")
                try:
                    result = await session.call_tool("import_media", arguments={"file_path": file_path})
                    print(f"  Result: {result.content[0].text}")
                    if "Successfully" in result.content[0].text:
                        success_count += 1
                except Exception as e:
                    print(f"  Failed: {e}")
            
            print(f"\nSummary: Successfully imported {success_count}/{len(files_to_import)} files.")

if __name__ == "__main__":
    asyncio.run(run())
