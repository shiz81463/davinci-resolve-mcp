import asyncio
import os
import sys
import json

# Add project root to sys.path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, project_root)

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def force_assemble():
    server_script = os.path.join(project_root, "src", "resolve_mcp_server.py")
    env = os.environ.copy()
    env["PYTHONPATH"] = project_root + os.pathsep + env.get("PYTHONPATH", "")

    server_params = StdioServerParameters(command=sys.executable, args=[server_script], env=env)

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            print("Opening project 'imax countdown'...")
            # We assume project is open or can be opened
            await session.call_tool("open_project", arguments={"name": "imax countdown"})

            # Staged Assets
            staging_dir = "/Users/ziconghuang/.gemini/antigravity/scratch/imax_staging"
            assets = [
                f"{staging_dir}/IMAX_wk01_fixed.mov",
                f"{staging_dir}/IMAX_wk03_fixed.mov",
                f"{staging_dir}/IMAX_Intro_Fixed.comp"
            ]
            
            # Original Assets that worked
            original_wk02 = "/Users/ziconghuang/Downloads/IMAX_Countdown/IMAX_Pt2/Blend File/IMAX_wk02_render.mov"
            original_nebula = "/Users/ziconghuang/Downloads/IMAX_Countdown/IMAX_Dabble/Background/nebula-668783.jpg"
            
            all_imports = assets + [original_wk02, original_nebula]

            print("Importing all assets (Force Mode)...")
            for asset in all_imports:
                if os.path.exists(asset):
                    print(f"Importing: {os.path.basename(asset)}")
                    try:
                        await session.call_tool("import_media", arguments={"file_path": asset})
                    except Exception as e:
                        print(f"  Failed to import: {e}")
                else:
                    print(f"  Missing file: {asset}")

            # Get Available Clips (Recursive)
            print("Listing Media Pool content...")
            available_clips = []
            try:
                result = await session.read_resource("resolve://media-pool-clips")
                content_text = result.contents[0].text
                try:
                    clips_data = json.loads(content_text)
                    available_clips = [c['name'] for c in clips_data if 'name' in c]
                    print(f"Available Clips in Project: {len(available_clips)} found")
                except:
                    print("  Failed to parse clip list JSON")
            except Exception as e:
                print(f"  Failed to list clips: {e}")

            # Define Sequence
            # 1. Intro (Comp)
            # 2. Dabble (Nebula)
            # 3. Wk01 (Fixed)
            # 4. Wk02 (Render)
            # 5. Wk03 (Fixed)
            # 6. Wk04 (Nebula - Placeholder)
            
            sequence = [
                {"name": "IMAX_Intro_Fixed", "fallback": "IMAX_Intro_Combined.comp", "type": "Intro"},
                {"name": "nebula-668783.jpg", "fallback": None, "type": "Dabble (Placeholder)"},
                {"name": "IMAX_wk01_fixed", "fallback": "IMAX_wk01_fixed.mov", "type": "Week 01"},
                {"name": "IMAX_wk02_render.mov", "fallback": "IMAX_wk02_render.mov", "type": "Week 02"},
                {"name": "IMAX_wk03_fixed", "fallback": "IMAX_wk03_fixed.mov", "type": "Week 03"},
                {"name": "nebula-668783.jpg", "fallback": None, "type": "Week 04 (Placeholder)"}
            ]

            # Create Timeline
            tl_name = "IMAX 80 Percent Sequence"
            print(f"Creating Timeline: {tl_name}")
            await session.call_tool("create_timeline", arguments={"name": tl_name})

            print("Assembling sequence...")
            added_count = 0
            for item in sequence:
                target = item["name"]
                # Fuzzy Find
                match = None
                for av in available_clips:
                    if target in av:
                        match = av
                        break
                
                if not match and item["fallback"]:
                    for av in available_clips:
                        if item["fallback"] in av:
                            match = av
                            break
                            
                if match:
                    print(f"Adding [{item['type']}]: {match}")
                    try:
                        await session.call_tool("add_clip_to_timeline", arguments={"clip_name": match})
                        added_count += 1
                    except Exception as e:
                        print(f"  Failed: {e}")
                else:
                    print(f"Missing asset for [{item['type']}]. Target: {target}")

            print(f"Done. Added {added_count}/{len(sequence)} clips.")

if __name__ == "__main__":
    asyncio.run(force_assemble())
