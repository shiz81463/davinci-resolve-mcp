import asyncio
import os
import sys
import json

# Add project root to sys.path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, project_root)

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def force_fix():
    print("Starting Timeline Repair...")
    
    server_script = os.path.join(project_root, "src", "resolve_mcp_server.py")
    env = os.environ.copy()
    env["PYTHONPATH"] = project_root + os.pathsep + env.get("PYTHONPATH", "")

    server_params = StdioServerParameters(command=sys.executable, args=[server_script], env=env)

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            # Switch to Edit Page
            await session.call_tool("switch_page", arguments={"page": "edit"})

            # Re-Import Media (To ensure valid handle)
            render_path = "/Users/ziconghuang/Downloads/IMAX_Countdown/IMAX_Pt2/Blend File/IMAX_wk02_vertical.mov"
            print(f"Re-Importing Media: {render_path}")
            await session.call_tool("import_media", arguments={"file_path": render_path})
            
            # Create NEW Timeline (avoid conflict with broken one)
            tl_name = "Vertical Countdown Final"
            print(f"Creating New Timeline: {tl_name}")
            await session.call_tool("create_timeline", arguments={"name": tl_name})
            
            # Add Clip
            print("Adding Clip to Timeline...")
            # Try to find specific name
            res = await session.read_resource("resolve://media-pool-clips")
            clips = json.loads(res.contents[0].text)
            
            target_clip = None
            for c in clips:
                if "wk02_vertical" in c.get('name', ''):
                    target_clip = c.get('name')
                    # Prefer the one with duration > 0 if possible?
                    # API listing might cache?
                    print(f"  Found candidate: {c.get('name')} (Duration: {c.get('duration')})")
            
            if not target_clip:
                target_clip = "IMAX_wk02_vertical" # Fallback guess
            
            print(f"Attempting to add: {target_clip}")
            try:
                await session.call_tool("add_clip_to_timeline", arguments={"clip_name": target_clip})
                print("✅ Clip added successfully.")
            except Exception as e:
                print(f"❌ Failed to add clip: {e}")
                
            print("Timeline Repair Complete.")

if __name__ == "__main__":
    asyncio.run(force_fix())
