import asyncio
import os
import sys
import subprocess
import time

# Add the project root to sys.path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, project_root)

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def run_import_script():
    print("Step 1: Running refined_import_imax.py to ensure assets are present...")
    import_script = os.path.join(project_root, "scripts", "refined_import_imax.py")
    try:
        process = subprocess.Popen(
            [sys.executable, import_script],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Stream output
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                print(f"  [Import] {output.strip()}")
                
        rc = process.poll()
        if rc != 0:
            print(f"Import script failed with exit code {rc}")
            return False
            
        print("Import completed successfully.\n")
        return True
    except Exception as e:
        print(f"Error running import script: {e}")
        return False

async def build_timeline():
    print("Step 2: Connecting to MCP Server for Timeline Construction...")
    
    # Setup server parameters
    server_script = os.path.join(project_root, "src", "resolve_mcp_server.py")
    python_exe = sys.executable
    
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
            
            # Open Project
            await session.call_tool("open_project", arguments={"name": "imax countdown"})
            
            # Debug: Dump Media Pool
            print("\n----- DEBUG: MEDIA POOL CONTENT -----")
            try:
                dump = await session.call_tool("dump_media_pool", arguments={})
                print(dump.content[0].text)
            except Exception as e:
                print(f"Failed to dump media pool: {e}")
            print("----- END DEBUG -----\n")

            # Create Timeline
            timeline_name = "IMAX Automated Sequence"
            print(f"Creating Timeline: {timeline_name}")
            try:
                # First try to delete if exists to start fresh?
                # delete_timeline(resolve, timeline_name) - available as tool?
                # We'll just create. If it fails, we assume it exists and we append to it?
                # Or we use a unique name?
                # Let's try creating.
                await session.call_tool("create_timeline", arguments={"name": timeline_name})
            except Exception as e:
                print(f"Timeline creation note (might likely exist): {e}")

            # Define Clips to Add (Order matters for V1, V2, V3 if we had tracks, 
            # but AppendToTimeline adds to the *end* of the active track usually, or sequential?
            # AppendToTimeline appends to the end of the timeline.
            # If we want tracks, we need to Manage Tracks.
            # The current API `add_clip_to_timeline` just uses `AppendToTimeline`.
            # This will put them all in sequence on V1 usually.
            # To Layer them, we need `AddTrack` or `SetTargetTrack`.
            # We don't have tools exposed for `SetTargetVideoTrack` yet.
            # Workaround: We will append them sequentially for now, as that's what 'Append' does. 
            # The user can then drag them.
            # BUT, to match the tutorial, they should be layered.
            # Since we can't layer programmatically easily yet, we'll append sequentially 
            # and the user will have all clips on the timeline to rearrange.
            
            clips_to_add = [
                "nebula-668783.jpg",
                "IMAX_wk01_render.mov",
                "IMAX_wk02_render.mov",
                "IMAX_wk03_render.mov",
                "IMAX_wk04_render.mov",
                "IMAX_Dabble_render.mov", # Assuming this existed
                "IMAX_Intro_Combined.comp" # Or without extension
            ]
            
            for clip in clips_to_add:
                print(f"Adding clip: {clip}")
                success = False
                try:
                    result = await session.call_tool("add_clip_to_timeline", arguments={"clip_name": clip})
                    if "Error" not in result.content[0].text:
                        print(f"  Result: {result.content[0].text}")
                        success = True
                    else:
                        print(f"  Initial attempt failed: {result.content[0].text}")
                except Exception as e:
                    print(f"  Failed: {e}")
                
                if not success:
                    # Try removing extension
                    name_no_ext = os.path.splitext(clip)[0]
                    if name_no_ext != clip:
                        print(f"  Retrying as {name_no_ext}...")
                        try:
                            result = await session.call_tool("add_clip_to_timeline", arguments={"clip_name": name_no_ext})
                            print(f"  Result: {result.content[0].text}")
                        except Exception as e:
                            print(f"  Retry failed: {e}")

if __name__ == "__main__":
    if asyncio.run(run_import_script()):
        asyncio.run(build_timeline())
