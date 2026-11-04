# Digital Eye Strain Helper

A small Windows desktop app that reminds you to rest your eyes, based on the 20-20-20 rule (every 20 minutes, look 20 feet away for 20 seconds). It sits in the system tray, shows a desktop notification on a configurable interval, can play a sound of your choice, and has a brightness slider. It was written as a student/coursework project to practise building a GUI application in Python.

## Features

- Start/stop reminder timer with a configurable interval (1-60 minutes) and custom message
- Desktop notifications, optionally with an uploaded `.wav`/`.mp3` sound
- Optional "start the reminder when mouse activity is detected" mode
- Screen brightness slider
- System tray icon (show/exit) so it can run in the background
- Settings are saved to a local JSON file on exit and validated on load

## Stack

- Python 3, Tkinter with `ttkbootstrap` for theming
- `plyer` (notifications), `pygame` (sound), `pystray` + `Pillow` (tray icon)
- `pynput` (mouse activity), `screen-brightness-control` (brightness)

## Running

```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

pip install -r requirements.txt
python src/App.py
```

On first run the app creates `src/config/config.json` with default settings and writes `eye_strain.log` in the working directory. Both are git-ignored.

## Project layout

- `src/App.py` - main window, reminder loop, tray icon, settings persistence
- `src/Utilities.py` - input validation, sound upload/selection, config load/save
- `src/assets/` - tray icon and sample notification sounds

## Status

Hobby project; tested only on Windows. Brightness control and notifications depend on platform support.
