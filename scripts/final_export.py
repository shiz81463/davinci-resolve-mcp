import asyncio
import os
import sys
import json
import time

# Add project root to sys.path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, project_root)

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def final_export():
    server_script = os.path.join(project_root, "src", "resolve_mcp_server.py")
    env = os.environ.copy()
    env["PYTHONPATH"] = project_root + os.pathsep + env.get("PYTHONPATH", "")

    server_params = StdioServerParameters(command=sys.executable, args=[server_script], env=env)

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            print("Opening project 'imax countdown'...")
            try:
                await session.call_tool("open_project", arguments={"name": "imax countdown"})
            except:
                pass # Already open hopefully

            # switch to edit page first
            await session.call_tool("switch_page", arguments={"page": "edit"})

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

            # Define Sequence with Fallbacks
            # Intro -> Dabble -> Wk01 -> Wk02 -> Wk03 -> Wk04
            sequence = [
                {"name": "IMAX_Intro_Fixed", "fallback": "nebula-668783.jpg", "type": "Intro"},
                {"name": "nebula-668783.jpg", "fallback": None, "type": "Dabble"},
                {"name": "IMAX_wk01_fixed", "fallback": "nebula-668783.jpg", "type": "Week 01"},
                {"name": "IMAX_wk02_render.mov", "fallback": "nebula-668783.jpg", "type": "Week 02"},
                {"name": "IMAX_wk03_fixed", "fallback": "nebula-668783.jpg", "type": "Week 03"},
                {"name": "IMAX_wk04_render.mov", "fallback": "nebula-668783.jpg", "type": "Week 04"}
            ]

            # Create Timeline
            tl_name = "IMAX Final Export Sequence"
            print(f"Creating Timeline: {tl_name}")
            try:
                await session.call_tool("create_timeline", arguments={"name": tl_name})
            except:
                # If exists, switch to it? Or assume newly created
                await session.call_tool("set_current_timeline", arguments={"name": tl_name})

            print("Assembling sequence...")
            for item in sequence:
                target = item["name"]
                match = None
                
                # Try target
                for av in available_clips:
                    if target in av:
                        match = av
                        break
                
                # Try fallback
                if not match and item["fallback"]:
                    for av in available_clips:
                        if item["fallback"] in av:
                            match = av
                            break
                            
                if match:
                    print(f"Adding [{item['type']}]: {match}")
                    try:
                        await session.call_tool("add_clip_to_timeline", arguments={"clip_name": match})
                    except Exception as e:
                        print(f"  Failed: {e}")
                else:
                    print(f"Missing asset for [{item['type']}]. No fallback available.")

            # EXPORT
            print("-" * 20)
            print("Preparing for Export...")
            
            # Switch to Deliver page
            await session.call_tool("switch_page", arguments={"page": "deliver"})
            
            # Get Presets
            try:
                presets_res = await session.read_resource("resolve://delivery/render-presets")
                # Parse presets if needed, typically returns list of dicts
                # For now, let's just try to use a standard one or the first one.
                # Actually server implementation of get_render_presets returns List[Dict]
                presets_data = json.loads(presets_res.contents[0].text)
                
                # Look for H.264
                target_preset = None
                for p in presets_data:
                    if "H.264" in p.get("name", ""):
                        target_preset = p["name"]
                        break
                
                if not target_preset and presets_data:
                    target_preset = presets_data[0]["name"] # First one
                    
                print(f"Selected Render Preset: {target_preset}")
                
                if target_preset:
                    # Clear Queue
                    await session.call_tool("clear_render_queue", arguments={})
                    
                    # Add Job
                    await session.call_tool("add_to_render_queue", arguments={"preset_name": target_preset})
                    
                    # Start Render
                    print("Starting Render...")
                    await session.call_tool("start_render", arguments={})
                    
                    # Monitor
                    rendering = True
                    while rendering:
                        status_res = await session.read_resource("resolve://delivery/render-queue/status")
                        status_data = json.loads(status_res.contents[0].text)
                        
                        # Check status of first job (or all)
                        # Implementation of get_render_queue_status returns dict showing status
                        # { "job_count": 1, "jobs": [...] }
                        
                        jobs = status_data.get("jobs", [])
                        if not jobs:
                            print("No jobs in queue?")
                            break
                            
                        job = jobs[0] # Assuming single job
                        status = job.get("status", "Unknown")
                        pct = job.get("percentage", 0)
                        
                        print(f"Render Status: {status} ({pct}%)")
                        
                        if status in ["Complete", "Cancelled", "Failed"]:
                            rendering = False
                            print(f"Render Finished with status: {status}")
                        else:
                            await asyncio.sleep(2)
                            
                else:
                    print("No render preset found!")
                    
            except Exception as e:
                print(f"Export failed: {e}")

if __name__ == "__main__":
    asyncio.run(final_export())
