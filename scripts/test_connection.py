
import asyncio
import os
import sys

# Add project root to sys.path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(project_root)

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def run():
    # Define server parameters
    # We use the same python interpreter running this script
    python_exe = sys.executable
    server_script = os.path.join(project_root, "src", "resolve_mcp_server.py")
    
    print(f"Starting server: {server_script}...")
    
    env = os.environ.copy()
    env["PYTHONPATH"] = project_root + os.pathsep + env.get("PYTHONPATH", "")

    server_params = StdioServerParameters(
        command=python_exe,
        args=[server_script],
        env=env
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            print("Connected to server process.")
            
            # Initialize
            await session.initialize()
            print("Initialized MCP session via stdio.")

            # List Tools
            print("\n--- Available Tools ---")
            tools = await session.list_tools()
            for tool in tools.tools:
                print(f"- {tool.name}: {tool.description}")

            # Example: Get Resolve Version (if available as resource or tool)
            # Checking resources first
            print("\n--- Checking Resources ---")
            resources = await session.list_resources()
            for resource in resources.resources:
                print(f"- {resource.name} ({resource.uri})")
                
            # Try to read version if available
            try:
                # Based on README, resolve://version might be available
                result = await session.read_resource("resolve://version")
                print(f"\nDaVinci Resolve Version: {result.contents[0].text}")
            except Exception as e:
                print(f"\nCould not read version: {e}")

if __name__ == "__main__":
    try:
        asyncio.run(run())
    except KeyboardInterrupt:
        print("Stopped.")
    except Exception as e:
        print(f"Error: {e}")
