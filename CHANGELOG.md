# Changelog

## Unreleased

- Correct canonical six-column Soroban geometry: lower beads stay below the
  divider, upper beads above; disjoint hit targets and contiguous active groups.
- Derive all bead state/geometry from validated digits; stop after one click hit.
- Ignore non-left clicks; add selected-column keyboard controls and clean exits.
- Replace ambiguous red-on-red state with cream active beads, spatial grouping,
  clearer wooden chambers, visible focus, place values and onscreen controls.
- Make imports side-effect free; add stdlib model/geometry/interaction tests,
  finite real pygame rendering smoke and bounded Ubuntu/Windows CI configuration.
- Pin pygame 2.6.1; document Windows venv setup and historical variants.

Local implementation only. Hosted CI, independent engineering review,
integration and release remain separate gates.
