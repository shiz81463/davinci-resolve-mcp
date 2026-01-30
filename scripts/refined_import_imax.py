import asyncio
import os
import sys
import subprocess

# Add the project root to sys.path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, project_root)

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# System files to ignore
IGNORE_FILES = {'.DS_Store', 'Thumbs.db'}

# Blender Path
BLENDER_PATH = "/Applications/Blender.app/Contents/MacOS/Blender"
RENDER_SCRIPT = os.path.join(project_root, "scripts", "render_blend.py")

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
                await session.call_tool("open_project", arguments={"name": "imax countdown"})
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
                
                # Filter files
                valid_files = [f for f in files if f not in IGNORE_FILES and not f.startswith('.')]
                
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
                
                # Process Files
                for file in valid_files:
                    full_path = os.path.join(root, file)
                    filename, ext = os.path.splitext(file)
                    ext = ext.lower()
                    
                    if ext == ".blend":
                        # Process Blend File
                        print(f"  Found Blend file: {file}")
                        # Check if render already exists
                        render_path = os.path.join(root, f"{filename}_render.mov")
                        if not os.path.exists(render_path):
                            print(f"    Rendering {file} via Blender...")
                            try:
                                # Run Blender Command
                                cmd = [
                                    BLENDER_PATH, 
                                    "-b", full_path, 
                                    "-P", RENDER_SCRIPT, 
                                    "--", render_path, "MOV"
                                ]
                                # Run synchronously
                                subprocess.check_call(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                                print("    Render complete.")
                            except Exception as e:
                                print(f"    Render failed: {e}")
                                continue
                        else:
                            print("    Render already exists, skipping render.")
                            
                        # Import the rendered file
                        if os.path.exists(render_path):
                            print(f"    Importing render: {os.path.basename(render_path)}")
                            try:
                                result = await session.call_tool("import_media", arguments={"file_path": render_path})
                                print(f"      Result: {result.content[0].text}")
                            except Exception as e:
                                print(f"      Import failed: {e}")
                                
                    elif ext == ".comp":
                        # Import Fusion Comp as Media
                        print(f"  Importing Fusion Comp: {file}")
                        try:
                            # Try ImportMedia first as it creates a clip
                            result = await session.call_tool("import_media", arguments={"file_path": full_path})
                            print(f"    Result: {result.content[0].text}")
                        except Exception as e:
                            print(f"    Failed ImportMedia: {e}")
                            # Fallback to fusion operation if needed (but usually we want a clip)
                            try:
                                result = await session.call_tool("import_fusion_comp", arguments={"path": full_path})
                                print(f"    Result (Fusion Load): {result.content[0].text}")
                            except Exception as e2:
                                print(f"    Failed Fusion Load: {e2}")
                            
                    elif ext in [".setting"]:
                        print(f"  Skipping Setting file: {file}")
                        
                    elif ext in [".mov", ".mp4", ".jpg", ".png", ".wav", ".mp3"]: # Basic media types
                         # Only import if it's NOT a render file we just made (ends in _render.mov)
                         # Although logic above handles .blend -> produces _render.mov
                         # If run again, valid_files will include _render.mov.
                         # We should probably skip importing _render.mov natively if we handle .blend?
                         # Or just let it import?
                         # Better: Import it.
                         
                         print(f"  Importing Media: {file}")
                         try:
                            result = await session.call_tool("import_media", arguments={"file_path": full_path})
                            print(f"    Result: {result.content[0].text}")
                         except Exception as e:
                            print(f"    Failed: {e}")

            print("\nRefined Import complete.")

if __name__ == "__main__":
    asyncio.run(run())
