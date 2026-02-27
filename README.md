# Desktop Clock (Windows)

A Windows desktop clock app with fullscreen display, timing modes, customizable text styles, and a frosted-glass control bar.

## Features

- Real-time clock display (`HH:MM:SS`)
- `Count Up` and `Count Down` modes
- Set current displayed time manually (`HH:MM:SS`)
- Custom text content
- Text style panel:
  - Time font size slider + numeric input
  - Text font size slider + numeric input
  - RGB color sliders + numeric inputs
- Background customization:
  - Select image or solid color background
  - Background scale slider (`20%` to `300%`) + numeric input
- Bottom frosted-glass style toolbar
- Mode display integrated directly in toolbar
- Toolbar hide/show:
  - Click `隐藏栏` to hide
  - Keep only one arrow button to restore toolbar
- Fullscreen toggle
- Packaged single-file `.exe` support

## Project Files

- `clock_app.py`: main app source code
- `CHANGELOG.md`: version history
- `dist/DesktopClock.exe`: packaged executable

## Requirements

- Python 3.12+
- Pillow (for robust image support and scaling)

Install dependencies:

```powershell
py -3 -m pip install pillow
```

## Run from Source

```powershell
py -3 clock_app.py
```

## Build EXE

```powershell
py -3 -m PyInstaller --noconfirm --clean --onefile --windowed --name DesktopClock --hidden-import PIL --hidden-import PIL.Image --hidden-import PIL.ImageTk clock_app.py
```

Output:

- `dist/DesktopClock.exe`

## Shortcuts

- `H`: Help
- `B`: Select background image
- `C`: Select background color
- `T`: Edit custom text
- `F`: Open style panel
- `M`: Switch mode
- `R`: Reset timer
- `S`: Pause/Resume timer
- `Esc`: Exit fullscreen
- `Q`: Quit app
