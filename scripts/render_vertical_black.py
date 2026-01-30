import bpy
import os
import sys

def process():
    scene = bpy.context.scene
    
    # 1. Resolution 9:16
    scene.render.resolution_x = 1080
    scene.render.resolution_y = 1920
    print("Set resolution to 1080x1920 (9:16)")
    
    # 2. World Black
    if scene.world and scene.world.node_tree:
        # Try to find Background node
        bg_node = None
        for node in scene.world.node_tree.nodes:
            if node.type == 'BACKGROUND':
                bg_node = node
                break
        
        if bg_node:
            bg_node.inputs[0].default_value = (0, 0, 0, 1) # Color Black
            bg_node.inputs[1].default_value = 0.0 # Strength 0
            print("Set World Background to Black (Strength 0)")
        else:
            print("Warning: No Background node found in World shader")
            
    # 3. Output Settings
    blend_path = bpy.data.filepath
    output_dir = os.path.dirname(blend_path)
    filename = os.path.splitext(os.path.basename(blend_path))[0]
    output_path = os.path.join(output_dir, f"{filename}_vertical.mov")
    
    scene.render.image_settings.file_format = 'FFMPEG'
    scene.render.ffmpeg.format = 'QUICKTIME'
    scene.render.ffmpeg.codec = 'H264'
    scene.render.filepath = output_path
    
    # 4. Hide Potential Background Objects
    # Heuristic: Hide objects with 'nebula', 'star', 'back', 'plane' in name EXCEPT if they are likely the main subject
    # We assume the main subject is the Countdown.
    for obj in bpy.data.objects:
        name_lower = obj.name.lower()
        if any(x in name_lower for x in ['nebula', 'star', 'bg', 'back', 'cloud', 'atmos']):
            print(f"Hiding object: {obj.name}")
            obj.hide_render = True
        
        # Also ensure Text is visible
        if obj.type == 'FONT':
            obj.hide_render = False

    print(f"Starting Render to: {output_path}")
    try:
        bpy.ops.render.render(animation=True)
        print("Render Finished Successfully.")
    except Exception as e:
        print(f"Render Failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    process()
