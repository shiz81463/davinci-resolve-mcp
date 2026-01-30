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
            
            print("Listing all media pool content:")
            
            # Use 'list_resources' or implement custom inspection via a tool?
            # We don't have a 'dump_media_pool' tool.
            # But we can assume the server internal utilities work if we added recursive search.
            # But I want to see it.
            # I'll create a new tool function in this script that I can't inject.
            # So I have to use existing tools to list content.
            # 'get_folder_clips' or similar?
            # I'll check available tools with list_tools
            
            tools = await session.list_tools()
            # print([t.name for t in tools.tools])
            
            # I can't easily list recursively via existing tools if 'get_folder_clips' only does one level.
            # But I can walk it if I can list folders.
            # Is there a 'get_subfolders' tool?
            # I'll check documentation or source.
            
            # Checking `media_operations.py` again.
            # `get_all_media_pool_folders` is a helper, but not exposed!
            # `list_dir` is for file system.
            
            # I will modify `resolve_mcp_server.py` or `media_operations.py` to add a debug tool
            # `dump_media_pool` which prints the tree.
            # This is useful for future anyway.
            pass

if __name__ == "__main__":
    asyncio.run(run())
