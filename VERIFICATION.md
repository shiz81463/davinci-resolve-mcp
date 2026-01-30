# DaVinci Resolve MCP Verification Checklist

Use this checklist to verify that your DaVinci Resolve MCP server is correctly installed, configured, and fully functional.

## 1. Prerequisites Check
> [!IMPORTANT]
> **DaVinci Resolve Studio (Paid Version) is REQUIRED.**
> The Free version does **not** support External Scripting, which is necessary for this tool to work.

- [ ] **DaVinci Resolve Studio** is installed and running.
    - *Note: The Free version may work for some features, but Studio is recommended for full API support.*
- [ ] **Python 3.6+** is installed (`python --version`).
- [ ] **External Scripting** is enabled in DaVinci Resolve:
    - Go to `DaVinci Resolve` -> `Preferences` -> `System` -> `General` -> `External Scripting Using` -> Select `Local`.

## 2. Installation Verification
- [ ] Project repository is cloned.
- [ ] Python virtual environment (`venv`) is created.
- [ ] Dependencies are installed (`pip install -r requirements.txt`).
- [ ] Environment variables are set correctly:
    - `RESOLVE_SCRIPT_API`
    - `RESOLVE_SCRIPT_LIB`
    - `PYTHONPATH`
    - *Tip: Run `./scripts/check-resolve-ready.sh` (macOS) or `scripts\check-resolve-ready.bat` (Windows) to verify these automatically.*

## 3. Server Startup Check
- [ ] Run the quick start script:
    - macOS: `./run-now.sh`
    - Windows: `run-now.bat`
- [ ] Verify output:
    - [ ] "DaVinci Resolve found" message appears.
    - [ ] "Starting MCP server..." message appears.
    - [ ] No immediate crash or error tracebacks.

## 4. Client Connection Verification (Cursor)
- [ ] Open Cursor settings -> `MCP`.
- [ ] Verify "davinci-resolve" server is listed with a green status indicator.
- [ ] If status is red/error:
    - Check the "Output" tab in Cursor and select "MCP" or "DaVinci Resolve" channel.
    - Verify absolute paths in `.cursor/mcp.json`.

## 5. Functional Verification (Natural Language)
Open a chat in Cursor/Claude and try these commands to verify specific capabilities.

### Basic Connection
- [ ] **Prompt:** "What is the current DaVinci Resolve version?"
    - **Expected Result:** Returns the correct version number (e.g., 18.6.x).
- [ ] **Prompt:** "What page is currently active?"
    - **Expected Result:** Returns "Edit", "Color", "Fusion", etc.

### Project Management
- [ ] **Prompt:** "List all available projects."
    - **Expected Result:** A list of project names from your database.
- [ ] **Prompt:** "What is the current project name?"
    - **Expected Result:** The name of the currently open project.

### Timeline Operations
- [ ] **Prompt:** "List all timelines in this project."
    - **Expected Result:** List of timeline names.
- [ ] **Prompt:** "Create a new timeline called 'Verification Test'."
    - **Expected Result:** A new empty timeline appears in the project.
- [ ] **Prompt:** "Switch to the 'Verification Test' timeline."
    - **Expected Result:** The active timeline changes.

### Marker Operations
- [ ] **Prompt:** "Add a blue marker at the current playhead with the note 'Check point'."
    - **Expected Result:** A blue marker appears on the timeline at the current position.
- [ ] **Prompt:** "List all markers on the current timeline."
    - **Expected Result:** Returns a list including the marker you just created.
- [ ] **Prompt:** "Delete the marker at the current position."
    - **Expected Result:** The marker is removed.

### Media Pool Operations
- [ ] **Prompt:** "List the contents of the root bin."
    - **Expected Result:** Lists clips/timelines in the master bin.
- [ ] **Prompt:** "Create a new bin called 'Test Bin'."
    - **Expected Result:** A new bin folder appears in the Media Pool.

## 6. Troubleshooting Verification
If any step failed:
- [ ] Check logs in `logs/` directory.
- [ ] Ensure DaVinci Resolve didn't crash or close.
- [ ] Restart the MCP server.
- [ ] Restart the AI Client (Cursor/Claude).
