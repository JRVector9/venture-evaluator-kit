# Changelog

## 1.1.1 · 2026-09-21 · Patch

### Fixed
- Renderer pattern check now uses `re.fullmatch`; an ID with a trailing newline (e.g. `"E1\n"`) previously
  passed validation and produced broken `id="source-E1\n"` anchors in the HTML. Regression test added (51 tests).

## 1.1.0 · 2026-09-21 · Report Edition

### Added
- White, independent consulting-report design with responsive navigation and print CSS.
- `scripts/render_report.py`: a Python 3.9+ standard-library renderer. No new pip dependency.
- `assets/report.schema.json`: strict report data contract and a matching bundled validator.
- Neutral `report.template.json` and explicitly fictional `report.sample.json`.
- A single, standalone HTML preview in `examples/venture-report-sample.html`.
- Current/conditional scorecard view, criterion-to-evidence navigation, expandable 12-dimension details.
- Evidence registry, metadata, executive summary, redesign, experiments, roadmap, budget, decision gates.
- Integer-KRW budget aggregation, recurring-month multiplication, incomplete-cost subtotal labeling.
- 32 renderer regression tests in addition to 18 existing installation tests; 11 browser checks.
- HTML-specific model evaluation cases (provided, not claimed as model-tested).

### Changed
- Default output of evaluation modes is a newly generated HTML report plus JSON.
- `md` and `no-save` opt out of file output; context edits still require explicit user instruction.
- Workspace initializer adds a `reports/` directory.
- Installer version and required files now cover report assets; existing backup/replacement behavior retained.

### Preserved
- Same skill name and local installation paths. Existing call syntax still works.
- Original `gsr-plus-1.0` rating rubric; report design does not change business scoring.
- Evidence boundaries, privacy rules, and current-versus-conditional distinction.
- No credential reading, background collection, auto-upload, automatic browser launch, or success guarantees.

### Validation limits
- Actual Claude/Codex loading and model behavior have not been exercised on a user's account.
- Browser checks used Chromium 144 through Playwright set_content; managed file:// navigation is restricted in the test environment.
- Safari, Firefox, Windows desktop behavior and physical PDF pagination have not been validated.
