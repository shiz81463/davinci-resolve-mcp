import asyncio
import os
import sys

# Add the project root to sys.path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, project_root)

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

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
            
            print("Listing Media Pool Bins...")
            try:
                result = await session.call_tool("list_media_pool_bins_tool")
                # Note: list_media_pool_bins is a resource, but I might have exposed it as a tool or need to read the resource
                # Wait, I didn't expose it as a tool in my previous edit, only `create_bin_path` and `set_current_bin`.
                # But `resolve_mcp_server.py` has `list_media_pool_bins` as a resource "resolve://media-pool-bins".
                # I should read the resource.
                pass
            except:
                pass

            # Read Resource
            try:
                result = await session.read_resource("resolve://media-pool-bins")
                print(result.contents[0].text)
            except Exception as e:
                print(f"Error reading bins: {e}")

if __name__ == "__main__":
    asyncio.run(run())
