import asyncio
import os
import sys

# Add the project root to sys.path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, project_root)

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Script content with correct steps
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
            
            # 1. Open Project
            print("Opening project 'imax countdown'...")
            try:
                await session.call_tool("open_project", arguments={"name": "imax countdown"})
            except Exception as e:
                print(f"Error opening project: {e}")
                return

            print("Creating IMAX Fusion Composition...")

            # 2. Setup: Create Fusion Clip (We'll assume user is in Media Pool or Timeline)
            # Actually, we need to create a Fusion Composition. 
            # The API doesn't have "Create Fusion Clip" exposed yet.
            # But we can try to work on the *current* open Fusion composition.
            # INSTRUCTION: User should ensure a Fusion composition is open or created.
            # Or we can try to use `create_bin` and assume user manually creates one/opens it?
            # Better: We can try to use `resolve.Fusion().NewComp()` if we had exposed it.
            # Since we only exposed `fusion_add_tool`, we assume we are working on the *current* comp.
            
            # Let's verify we have a current comp?
            # We don't have a tool to "get current comp name", but tools will fail if no comp.
            
            # STEP 1: Background (Atmosphere)
            print("1. Creating Background (Atmosphere)...")
            await session.call_tool("fusion_add_tool", arguments={"tool_name": "Background", "x": 0, "y": 0})
            # Rename isn't exposed, but we can find it by "Background1" usually. 
            # NOTE: Tool names increment. If the comp is empty, it's Background1.
            bg_main = "Background1" 
            
            # Set Deep Blue
            await session.call_tool("fusion_set_input", arguments={"tool_name": bg_main, "input_id": "TopLeftRed", "value": 0.0})
            await session.call_tool("fusion_set_input", arguments={"tool_name": bg_main, "input_id": "TopLeftGreen", "value": 0.1})
            await session.call_tool("fusion_set_input", arguments={"tool_name": bg_main, "input_id": "TopLeftBlue", "value": 0.3})
            # Gradient
            await session.call_tool("fusion_set_input", arguments={"tool_name": bg_main, "input_id": "Type", "value": 1}) # 1 = Gradient? Verify values. Usually 0=Solid.

            # STEP 2: The Rings
            print("2. Creating Rings...")
            await session.call_tool("fusion_add_tool", arguments={"tool_name": "Background", "x": 2, "y": 0})
            ring_bg = "Background2"
            await session.call_tool("fusion_set_input", arguments={"tool_name": ring_bg, "input_id": "TopLeftRed", "value": 0.6}) # Light Blue
            await session.call_tool("fusion_set_input", arguments={"tool_name": ring_bg, "input_id": "TopLeftGreen", "value": 0.8})
            await session.call_tool("fusion_set_input", arguments={"tool_name": ring_bg, "input_id": "TopLeftBlue", "value": 1.0})
            
            await session.call_tool("fusion_add_tool", arguments={"tool_name": "EllipseMask", "x": 2, "y": -1})
            ring_mask = "Ellipse1"
            await session.call_tool("fusion_set_input", arguments={"tool_name": ring_mask, "input_id": "Solid", "value": 0})
            await session.call_tool("fusion_set_input", arguments={"tool_name": ring_mask, "input_id": "BorderWidth", "value": 0.005})
            await session.call_tool("fusion_set_input", arguments={"tool_name": ring_mask, "input_id": "Width", "value": 0.7})
            await session.call_tool("fusion_set_input", arguments={"tool_name": ring_mask, "input_id": "Height", "value": 0.7})
            
            await session.call_tool("fusion_connect", arguments={"out_tool": ring_mask, "in_tool": ring_bg, "in_id": "EffectMask"})

            # STEP 3: Countdown Timer
            print("3. Creating Timer...")
            await session.call_tool("fusion_add_tool", arguments={"tool_name": "TextPlus", "x": 4, "y": 0})
            text_node = "Text1"
            await session.call_tool("fusion_set_input", arguments={"tool_name": text_node, "input_id": "Size", "value": 0.2})
            # Expression: ceil(10 - (time/24))
            await session.call_tool("fusion_set_expression", arguments={"tool_name": text_node, "input_id": "StyledText", "expression": "ceil(10 - (time/24))"})

            # STEP 4: Sweep
            print("4. Creating Sweep...")
            await session.call_tool("fusion_add_tool", arguments={"tool_name": "Background", "x": 6, "y": 0})
            sweep_bg = "Background3"
            await session.call_tool("fusion_set_input", arguments={"tool_name": sweep_bg, "input_id": "TopLeftAlpha", "value": 0.5})
            
            await session.call_tool("fusion_add_tool", arguments={"tool_name": "RectangleMask", "x": 6, "y": -1})
            sweep_mask = "Rectangle1"
            # Set Angle Expression: (-360 * (time / 24)) % 360
            # Wait, Angle input ID is "Angle"
            await session.call_tool("fusion_set_expression", arguments={"tool_name": sweep_mask, "input_id": "Angle", "expression": "-360 * (time/24)"})
            # Pivot Bottom Center? Pivot X/Y. Center is 0.5, 0.5. Bottom Center is 0.5, 0.0.
            # But Rectangle mask pivot is relative to center.
            # Actually, simpler to just rotate the mask.
            
            await session.call_tool("fusion_connect", arguments={"out_tool": sweep_mask, "in_tool": sweep_bg, "in_id": "EffectMask"})

            # STEP 5: Merge All
            print("5. Compositing...")
            # Merge 1: Rings over BG
            await session.call_tool("fusion_add_tool", arguments={"tool_name": "Merge", "x": 2, "y": 2})
            merge1 = "Merge1"
            await session.call_tool("fusion_connect", arguments={"out_tool": bg_main, "in_tool": merge1, "in_id": "Background"})
            await session.call_tool("fusion_connect", arguments={"out_tool": ring_bg, "in_tool": merge1, "in_id": "Foreground"})
            
            # Merge 2: Sweep over previous
            await session.call_tool("fusion_add_tool", arguments={"tool_name": "Merge", "x": 6, "y": 2})
            merge2 = "Merge2"
            await session.call_tool("fusion_connect", arguments={"out_tool": merge1, "in_tool": merge2, "in_id": "Background"})
            await session.call_tool("fusion_connect", arguments={"out_tool": sweep_bg, "in_tool": merge2, "in_id": "Foreground"})
            
            # Merge 3: Text over previous
            await session.call_tool("fusion_add_tool", arguments={"tool_name": "Merge", "x": 4, "y": 4})
            merge3 = "Merge3"
            await session.call_tool("fusion_connect", arguments={"out_tool": merge2, "in_tool": merge3, "in_id": "Background"})
            await session.call_tool("fusion_connect", arguments={"out_tool": text_node, "in_tool": merge3, "in_id": "Foreground"})

            # STEP 6: Blip (Glow)
            print("6. Adding Blip...")
            await session.call_tool("fusion_add_tool", arguments={"tool_name": "Glow", "x": 4, "y": 6})
            glow = "Glow1"
            await session.call_tool("fusion_set_expression", arguments={"tool_name": glow, "input_id": "Glow", "expression": "iif((time % 24) < 2, 0.8, 0)"})
            # Depending on Glow node version, input might be "Glow" or "Brightness" or "Source".
            # "Glow" usually controls blend. "Gain" controls brightness.
            # Let's try Gain?
            await session.call_tool("fusion_set_expression", arguments={"tool_name": glow, "input_id": "Gain", "expression": "iif((time % 24) < 2, 0.8, 0)"})

            await session.call_tool("fusion_connect", arguments={"out_tool": merge3, "in_tool": glow, "in_id": "Input"})
            
            # MediaOut
            print("Connecting to MediaOut...")
            media_out = "MediaOut1" # Usually exists
            await session.call_tool("fusion_connect", arguments={"out_tool": glow, "in_tool": media_out, "in_id": "Input"})
            
            print("IMAX Countdown Composition created successfully!")

if __name__ == "__main__":
    asyncio.run(run())
