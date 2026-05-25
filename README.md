# Space Haven Save Editor

A desktop save file editor for [Space Haven](https://bugbyte.fi/spacehaven/), the space colony sim by Bugbyte. If you want to give your crew a fighting chance, unlock research, or recover a run that went sideways, this tool lets you do that without touching raw XML.

## What you can edit

- **Crew** – rename characters, adjust stats (health, food, rest, mood, and more), skills, traits, conditions, and inter-crew relationships
- **Ships** – rename ships, adjust grid dimensions, and add or remove ships from your fleet
- **Storage** – browse each ship's storage containers and change item quantities
- **Research** – view the state of every technology and mark any of them as complete
- **Globals** – change game-wide values such as credits

## Download

Pre-built binaries are available on the [Releases](../../releases) page. Download the zip for your platform and extract it.

| Platform | File | Requirement |
|---|---|---|
| macOS | `SpaceHaven-Save-Editor-macos.zip` | Apple Silicon (M1 or later) |
| Windows | `SpaceHaven-Save-Editor-windows.zip` | Windows 10/11, x64 |

The macOS build runs on Apple Silicon only. Intel Mac users need to run from source (see below).

**macOS Gatekeeper warning**

Because the app is not notarized, macOS will block it on first launch with a message saying the developer cannot be verified. To allow it:

1. Try to open the app — it will be blocked.
2. Open **System Settings → Privacy & Security** and scroll down.
3. You should see a message about the blocked app. Click **Open Anyway**.
4. Confirm in the dialog that follows.

You only need to do this once.

## Setup (from source)

**Prerequisites:** Python 3.9+

```bash
git clone https://github.com/xLPMG/SpaceHaven-Save-Editor.git
cd SpaceHaven-Save-Editor
python -m venv .venv
source .venv/bin/activate       # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Running

```bash
python main.py
```

## Usage

1. Launch the editor and use **File → Open** (or drag your save file onto the window) to load a save.
2. Space Haven save files are named `game` and live inside numbered slot folders in the game's save directory. The exact path on your system is shown in the game's main menu under save management.
3. Use the tabs on the left to navigate between sections and make your changes.
4. Save with **File → Save** or **Ctrl+S**. A timestamped backup of the original file is created automatically before anything is written to disk.

Keep a manual backup before making sweeping changes — the backup the editor creates covers you for a single session, not for repeated overwrites.

## Running tests

```bash
pytest
```

