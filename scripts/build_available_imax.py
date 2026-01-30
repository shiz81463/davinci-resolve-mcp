import asyncio
import os
import sys

# Add project root to sys.path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, project_root)

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def build_available():
    server_script = os.path.join(project_root, "src", "resolve_mcp_server.py")
    env = os.environ.copy()
    env["PYTHONPATH"] = project_root + os.pathsep + env.get("PYTHONPATH", "")

    server_params = StdioServerParameters(command=sys.executable, args=[server_script], env=env)

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # Open Project
            print("Opening project 'imax countdown'...")
            try:
                await session.call_tool("open_project", arguments={"name": "imax countdown"})
            except Exception as e:
                print(f"Error opening project: {e}")
                return
            
            # Asset list to import (Absolute paths)
            base_dir = "/Users/ziconghuang/Downloads/IMAX_Countdown"
            assets = [
                f"{base_dir}/IMAX_Pt1/Blend File/IMAX_wk01_render.mov",
                f"{base_dir}/IMAX_Pt2/Blend File/IMAX_wk02_render.mov", # Current one (partial/full)
                f"{base_dir}/IMAX_Pt3/Blend File/IMAX_wk03_render.mov",
                f"{base_dir}/IMAX_Pt4/Blend File/IMAX_wk04_render.mov",
                f"{base_dir}/IMAX_Dabble/Background/nebula-668783.jpg",
                f"{base_dir}/IMAX_Pt5/Comp files/IMAX_Intro_Combined.comp"
            ]

            print("Importing available assets...")
            for asset in assets:
                if os.path.exists(asset):
                    print(f"Importing: {os.path.basename(asset)}")
                    try:
                        await session.call_tool("import_media", arguments={"file_path": asset})
                    except Exception as e:
                        print(f"  Failed to import: {e}")
                else:
                    print(f"Skipping missing asset: {asset}")

            # Create Timeline
            tl_name = "IMAX Assembled Sequence"
            print(f"Creating Timeline: {tl_name}")
            try:
                await session.call_tool("create_timeline", arguments={"name": tl_name})
            except Exception as e:
                print(f"Timeline creation note: {e}")

            # Debug: List all clips
            print("Listing Media Pool content...")
            try:
                # Note: list_media_pool_clips is a RESOURCE, not a tool
                # URI: resolve://media-pool-clips
                result = await session.read_resource("resolve://media-pool-clips")
                # result.contents is a list of ResourceContent
                import json
                # The server returns a list of dicts, but read_resource returns text usually?
                # The MCP resource implementation in python-sdk handles serialization.
                # Let's see what we get.
                content_text = result.contents[0].text
                print(f"Clips raw content: {content_text}")
                
                 # Parse if it's JSON string representation
                try:
                    # It might be a python list string or JSON
                    clips_data = json.loads(content_text)
                    available_clips = [c['name'] for c in clips_data if 'name' in c]
                    print(f"Available Clip Names: {available_clips}")
                except:
                    # Fallback if not valid JSON
                    available_clips = []
                    
            except Exception as e:
                print(f"Failed to list clips: {e}")
                available_clips = []

            # Add Clips
            # We will search available_clips for matches
            desired_clips = [
                "nebula-668783", 
                "IMAX_wk01_render", # Fails import
                "IMAX_wk02_render", # Success
                "IMAX_wk03_render", # Fails import
                "IMAX_wk04_render", # Corrupt
                "IMAX_Intro_Combined"
            ]
            
            print("Assembling sequence...")
            count = 0
            for desired in desired_clips:
                # Find matching clip in pool
                match = None
                for av in available_clips:
                    if desired in av: # Simple substring match, e.g. "IMAX_wk01_render" in "IMAX_wk01_render.mov"
                        match = av
                        break
                
                if match:
                    print(f"Adding clip: {match}")
                    try:
                         # For nebula, add it multiple times if it was a placeholder? 
                         # But let's just add what we have.
                        result = await session.call_tool("add_clip_to_timeline", arguments={"clip_name": match})
                        print(f"  Result: {result.content[0].text}")
                        count += 1
                    except Exception as e:
                        print(f"  Failed: {e}")
                else:
                    print(f"Skipping missing clip: {desired}")

            if count > 0:
                print(f"Successfully assembled {count} clips into timeline '{tl_name}'.")
            else:
                print("Warning: No clips were added to the timeline.")

if __name__ == "__main__":
    asyncio.run(build_available())
