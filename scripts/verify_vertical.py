import asyncio
import os
import sys
import json

# Add project root to sys.path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, project_root)

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def verify():
    server_script = os.path.join(project_root, "src", "resolve_mcp_server.py")
    env = os.environ.copy()
    env["PYTHONPATH"] = project_root + os.pathsep + env.get("PYTHONPATH", "")

    server_params = StdioServerParameters(command=sys.executable, args=[server_script], env=env)

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            print("--- Verification Report ---")
            
            # 1. Check Resolution
            w_res = await session.call_tool("get_project_setting", arguments={"setting_name": "timelineResolutionWidth"})
            h_res = await session.call_tool("get_project_setting", arguments={"setting_name": "timelineResolutionHeight"})
            
            w = w_res.content[0].text
            h = h_res.content[0].text
            print(f"Project Resolution: {w} x {h}")
            
            if w == "1080" and h == "1920":
                print("✅ 9:16 Vertical Format Confirmed.")
            else:
                print("❌ Resolution Mismatch!")

            # 2. Check Timeline & Clips
            try:
                tl_res = await session.read_resource("resolve://current-timeline")
                tl_info = json.loads(tl_res.contents[0].text)
                print(f"Current Timeline: {tl_info.get('name', 'Unknown')}")
                
                clips_res = await session.read_resource("resolve://timeline-clips")
                clips = json.loads(clips_res.contents[0].text)
                
                found_vertical = False
                for c in clips:
                    print(f"  - Clip: {c.get('name')} (Duration: {c.get('duration')} frames)")
                    if "vertical" in c.get('name', '').lower():
                        found_vertical = True
                        
                if found_vertical:
                    print("✅ Vertical Asset Found on Timeline.")
                else:
                    print("⚠️ Vertical Asset NOT Found on Timeline!")
                    
            except Exception as e:
                print(f"Error checking timeline: {e}")
                
            print("---------------------------")

if __name__ == "__main__":
    asyncio.run(verify())
