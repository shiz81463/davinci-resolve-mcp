# DaVinci Resolve MCP: Natural Language Control Guide

This guide explains how to control DaVinci Resolve using natural language commands with your AI Assistant (Cursor, Claude Desktop).

## Getting Started

> [!IMPORTANT]
> **Requirement:** You must use **DaVinci Resolve Studio** (Paid Version). The Free version does not support the external connections required.

1. **Ensure DaVinci Resolve is running** and a project is open.
2. **Start the MCP Server** (if not running automatically via Cursor/Claude config).
3. **Open a Chat** in your AI Assistant.

## Natural Language Commands

You can speak to DaVinci Resolve naturally. The AI understands context, so you don't always need exact command syntax. Here are examples of what you can do:

### 🔍 Discovery & Status
Ask about the current state of the application.
- "What project is currently open?"
- "Which page am I on?" (Edit, Color, etc.)
- "What is the timeline frame rate?"
- "List all timelines in this project."
- "Show me all bins in the media pool."

### 🎬 Timeline Management
Create and organize timelines.
- "Create a new timeline called 'Social Media Cut'."
- "Switch to the 'Main Assembly' timeline."
- "Create a timeline starting at 01:00:00:00."
- "Duplicate the current timeline."

### 📍 Markers & Notes
Add comments and markers for review or editing.
- "Add a blue marker here saying 'Fix color grade'."
- "Put a red marker at 01:00:10:00 for 'Cut point'."
- "List all markers directly on the timeline."
- "Delete the marker at the current playhead."
- "Find all blue markers."

### 🎞️ Media Management
Organize your footage.
- "Create a bin called 'Interviews'."
- "Import 'C:/Footage/Clip01.mov' into the 'Raw Footage' bin."
- "Move all selected clips to the 'Selects' bin."
- "List all clips in the 'Audio' bin."

### 🔧 Playback & Transport
Control the playback head.
- "Go to timecode 01:00:30:15."
- "Jump to the start of the timeline."
- "Move forward 10 frames."

## Power User Tips

### Chaining Commands
You can ask for multiple things at once:
- "Create a new timeline called 'Review', switch to it, and add a marker at the start saying 'Ready'."

### Intelligent Context
The assistant knows "here" usually means the current playhead position.
- "Add a marker *here*."

### Troubleshooting Responses
- **"I can't find that project/timeline"**: Check spelling. Names are case-sensitive in some contexts, though the AI tries to handle this.
- **"DaVinci Resolve is not reachable"**: Ensure the application didn't crash and scripting is enabled in Preferences.
- **"Action failed"**: Check if the requested action is possible in the current Page (e.g., some detailed editing commands only work on the Edit page).

## Example Workflow
Try this sequence to test the full loop:
1. "Create a project called 'MCP Demo'."
2. "Create a bin named 'Footage'."
3. "Create a timeline named 'First Cut'."
4. "Add a green marker at the start saying 'Intro'."
5. "Go to 5 seconds in."
6. "Add a red marker saying 'Action starts'."
