# Changelog

## 0.1.0 source candidate — 2026-10-26

- [PR #1](https://github.com/suttonwilliamd/abacus/pull/1): correct canonical
  six-column Soroban geometry. Lower beads now stay below the divider and
  upper beads above, with disjoint hit targets and contiguous active groups;
  previously lower beads crossed the divider and clicking 4→1 could yield 6.
- Derive all bead state/geometry from validated digits; stop after one click hit.
- Ignore non-left clicks; add selected-column keyboard controls and clean exits.
- Replace ambiguous red-on-red state with cream active beads, spatial grouping,
  clearer wooden chambers, visible focus, place values and onscreen controls.
- Make imports side-effect free; add stdlib model/geometry/interaction tests,
  finite real pygame rendering smoke and bounded Ubuntu/Windows CI configuration.
- Initialize only display/font and clean up partial initialization failures;
  previously broad pygame initialization attempted to start unused audio.
- Pin pygame 2.6.1; document Windows venv setup and historical variants.
- Source-release preparation: record actual hosted qualification and clarify
  that headless-smoke environment settings must not leak into the interactive
  PowerShell session. No runtime or test behavior changed in this preparation.

Independent engineering and rendered-design review completed; the implementation
merged with successful Ubuntu/Windows Python 3.11/3.13 test/render jobs. The
canonical source archive requires Python and pygame; it is not a standalone EXE.
Physical-device/DPI/screen-reader acceptance is not claimed. A source version or
tag is not a published GitHub Release; publication remains a separate gate.
