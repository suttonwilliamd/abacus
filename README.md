# Abacus — Six Places

A small pygame desktop Soroban for nonnegative decimal integers **0–999999**.
The canonical application is **`abacus.py`**. Each column has one upper bead
worth five and four lower beads worth one. Only beads moved toward the divider
count. Cream beads are active; red beads are inactive. Position, not just color,
communicates the state. The outlined column is selected for keyboard input.

## Windows setup (Python 3.11 or 3.13)

Open PowerShell in this folder with Python installed:

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe abacus.py
```

Use `py -3.11` instead if that is your installed version. No activation or
PowerShell execution-policy changes are necessary. On Linux, use
`python3 -m venv .venv`, then `.venv/bin/python` for the same commands.
Runtime dependency: pygame 2.6.1 (pinned; locally verified on Linux Python 3.13).

## Controls

| Input | Action |
| --- | --- |
| Left / Right | Select column; stop at the ends |
| 0–9 (top row or numeric keypad) | Set selected digit |
| Space | Toggle the selected upper bead (five) |
| Up / Down | Increase / decrease lower count, clamped to 0–4; no carry |
| R | Reset all digits to zero, retaining selection |
| Escape / window close | Exit cleanly |
| Left-click upper bead | Select its column and toggle only that upper bead |
| Left-click inactive lower bead i | Activate lower beads 0 through i |
| Left-click active lower bead i | Deactivate i through 3 (count becomes i) |

Lower beads are indexed from the divider downward. Clicking elsewhere or using
other mouse buttons does nothing. The footer shows each digit times its place
value; the large counter shows their sum, with no hidden accumulator.

## Tests and finite rendering smoke

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
$env:SDL_VIDEODRIVER = "dummy"
$env:SDL_AUDIODRIVER = "dummy"
.\.venv\Scripts\python.exe render_smoke.py --output artifacts
```

The smoke creates four **actual pygame-rendered** PNGs (zero, four, nine,
123456) and a sanitized JSON manifest. It exercises queued keyboard/mouse/exit
events and regresses the former overlapping-hit sequence using centers observed
from the renderer. It is finite and does not launch the interactive loop.
Unit tests exhaust local digit geometry and every cross-column state pair,
all lower-click transitions, place totals, bounds and import safety. Both entry
points initialize only display and font, not unused audio/mixer subsystems.
Lifecycle regressions observe live display/font with mixer uninitialized and
verify cleanup even when display or font setup partially fails.

CI is configured for standard Ubuntu/Windows runners and Python 3.11/3.13,
with bounded jobs and seven-day synthetic PNG/JSON artifacts. Configuration is
not proof those hosted jobs have run. SDL dummy rendering is not physical
device or interactive Windows acceptance.

## Scope and historical experiments

`abacus_baby.py`, `abacus_realistic.py`, and `accumulator.py` are **historical
experiments**, unchanged and not covered by the canonical app's correctness
claims or tests. Run `abacus.py` for the corrected Soroban.

This is a fixed-size 1000×740 desktop window, not a responsive/mobile app,
training game, standalone EXE, or OS screen-reader-accessible UI. Small displays
or aggressive desktop scaling may not fit it. No physical Windows-device
acceptance is claimed. No audio, networking, telemetry, paid assets, personal
data or state persistence is added. Fonts use pygame's bundled default font;
wood and beads are drawn primitives, with no external asset downloads.

## Credits

Original project based on code from Gippity (Claude Code). Corrected geometry,
keyboard operation and visual presentation contributed by BobRoss.bot/Paperclip.
