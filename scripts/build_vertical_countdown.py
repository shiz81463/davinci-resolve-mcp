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

async def build_vertical():
    # 1. Wait for Render
    render_path = "/Users/ziconghuang/Downloads/IMAX_Countdown/IMAX_Pt2/Blend File/IMAX_wk02_vertical.mov"
    print(f"Waiting for Blender render: {render_path}")
    
    # Wait max 20 minutes (1200s)
    timeout = 1200 
    start_time = time.time()
    
    print(f"Waiting for render (Timeout: {timeout}s)...")
    
    while True:
        if time.time() - start_time > timeout:
            print("Timeout waiting for render.")
            return
            
        if os.path.exists(render_path):
            size = os.path.getsize(render_path)
            # Must be > 1KB to be considered "started writing content"
            if size > 1000:
                break
        
        print(".", end="", flush=True)
        await asyncio.sleep(10)
        
    print("\nRender file found with content > 1KB!")
    
    # Wait for file to stabilize (Blender writes continuously)
    last_size = -1
    stable_count = 0
    while stable_count < 3:
        current_size = os.path.getsize(render_path)
        if current_size == last_size and current_size > 0:
            stable_count += 1
        else:
            last_size = current_size
            stable_count = 0
        await asyncio.sleep(5) # slower poll during write
    print(f"Render stable. Size: {last_size/1024/1024:.2f} MB")

    # 2. Connect to Resolve
    server_script = os.path.join(project_root, "src", "resolve_mcp_server.py")
    env = os.environ.copy()
    env["PYTHONPATH"] = project_root + os.pathsep + env.get("PYTHONPATH", "")

    server_params = StdioServerParameters(command=sys.executable, args=[server_script], env=env)

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            # Switch to Edit Page
            await session.call_tool("switch_page", arguments={"page": "edit"})

            # 3. Configure Project Settings (Vertical 9:16)
            print("Configuring Project Resolution to 1080x1920...")
            await session.call_tool("set_project_setting", arguments={"setting_name": "timelineResolutionWidth", "setting_value": "1080"})
            await session.call_tool("set_project_setting", arguments={"setting_name": "timelineResolutionHeight", "setting_value": "1920"})
            
            # 4. Import Media
            print("Importing Vertical Render...")
            await session.call_tool("import_media", arguments={"file_path": render_path})
            
            # 5. Create Timeline
            tl_name = "Vertical Countdown"
            print(f"Creating Timeline: {tl_name}")
            try:
                await session.call_tool("create_timeline", arguments={"name": tl_name})
            except:
                pass # Already exists?

            # 6. Add Clip
            print("Adding Clip...")
            clip_name = "IMAX_wk02_vertical" # Usually filename without extension? Or with?
            # Try both
            try:
                await session.call_tool("add_clip_to_timeline", arguments={"clip_name": clip_name})
            except:
                await session.call_tool("add_clip_to_timeline", arguments={"clip_name": clip_name + ".mov"})
            
            print("Timeline Assembly Complete.")
            
            # 7. Attempt Export (Manual Instructions fallback)
            print("Attempting to cue export...")
            try:
                # We know GetRenderSettings fails on GetPresets, so we might skip this or try specific addition
                # If we just add to render queue without preset?
                # add_to_render_queue requires preset_name.
                # If we can't get presets, we can't get a valid name guaranteed.
                # User asked to "export them in the end".
                # I'll try "H.264 Master" blindly.
                res = await session.call_tool("add_to_render_queue", arguments={"preset_name": "H.264 Master"})
                if "error" not in res.content[0].text.lower():
                    await session.call_tool("start_render", arguments={})
                    print("Render Started via Automation!")
                else:
                    print("Manual Render Required (API Error).")
            except Exception as e:
                print(f"Could not trigger automated render: {e}")
                print("\nPlease manually render 'Vertical Countdown' timeline in Deliver page.")

if __name__ == "__main__":
    asyncio.run(build_vertical())
