import bpy
import sys
import os

# Get arguments after "--"
argv = sys.argv
if "--" in argv:
    args = argv[argv.index("--") + 1:]
else:
    args = []

if len(args) < 2:
    print("Usage: blender -b file.blend -P render_blend.py -- <output_path> <format>")
    # We will just try to render to the same directory with _render suffix if arguments missing
    pass

# We expect the blend file to be already open (loaded via command line args before -P)

def setup_render(output_path):
    scene = bpy.context.scene
    
    # Set output format to QuickTime / H.264
    scene.render.image_settings.file_format = 'FFMPEG'
    scene.render.ffmpeg.format = 'QUICKTIME'  # Correct enum
    scene.render.ffmpeg.codec = 'H264'
    scene.render.ffmpeg.constant_rate_factor = 'MEDIUM'
    scene.render.ffmpeg.audio_codec = 'AAC'
    
    # Resolution (Keep original or force HD)
    # scene.render.resolution_x = 1920
    # scene.render.resolution_y = 1080
    
    # Set output path
    scene.render.filepath = output_path
    
    print(f"Render settings configured. Output: {output_path}")

def render():
    print("Starting render...")
    try:
        bpy.ops.render.render(animation=True, write_still=True)
        print("Render complete.")
    except Exception as e:
        print(f"Render failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    try:
        # Determine output path
        blend_file_path = bpy.data.filepath
        if not blend_file_path:
            print("Error: No blend file loaded.")
            sys.exit(1)
            
        directory = os.path.dirname(blend_file_path)
        filename = os.path.splitext(os.path.basename(blend_file_path))[0]
        
        # Output file: same folder, filename + "_render"
        output_path = os.path.join(directory, f"{filename}_render.mov")
        
        setup_render(output_path)
        render()
    except Exception as e:
        print(f"Script error: {e}")
        sys.exit(1)
