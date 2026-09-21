# Venture Evaluator 1.1.0 — Validation report

Date: 2026-09-21. These results describe checks actually run on this release in an isolated Linux container. They do not constitute a guarantee of business judgment, user-account installation, or investment performance.

## Summary

| Check | Result |
|---|---|
| Existing installer and workspace unit tests | 18 / 18 passed |
| New HTML renderer unit tests | 32 / 32 passed |
| Combined Python standard-library suite | **50 / 50 passed** |
| Chromium interaction / responsive / print-style groups | **11 / 11 passed** |
| Upgrade from the original supplied v1.0.0 archive | Passed on both isolated Claude and Codex installation paths |
| Final ZIP extraction / install / check / render | Passed; see `test-results/release-check.json` |
| Real Claude/Codex model execution | Not performed |
| Model evaluation scenarios | 12 existing + 6 HTML-specific cases supplied; not run against hosted models |

## Reproduce standard-library tests

From the extracted kit root, using Python 3.9+:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v
```

The release test runtime and count are recorded in `test-results/unit-tests.log`. No third-party package is needed for these 50 tests. The scripts target Python 3.9+, but this release did not execute a multi-version Python compatibility matrix.

The suite checks installer safety, project/user scopes, backups, integrity, refusal of symlinks and invalid targets, Unicode and space paths, context preservation, report schema validation, unknown metrics, source IDs, conditional ratings, all internal anchors, HTML escaping, safe source links, offline assets, recurring-budget arithmetic, incomplete budgets, exclusive creation, and report rendering outside the installed skill directory.

## Browser checks

Chromium 144.0.7559.96 with Playwright loaded the generated, standalone sample document using `page.set_content(html)`. Direct `file://` navigation is restricted by the managed browser environment, so **double-click/file-URL opening was not exercised**. The document has no external asset dependency.

The optional QA script is `tests/browser_smoke.py`. Playwright and a Chromium executable are only needed for this development check, not for installation, report generation, or reading HTML.

```bash
python3 tests/browser_smoke.py --chromium /path/to/chromium --output-dir /tmp/venture-browser-qa
```

Eleven groups passed: initial content and progressive enhancement; contents navigation and active section; current/conditional toggle; criterion links opening collapsed evidence and scrolling; expand/collapse; source references; widths 1440 / 1024 / 768 / 390 / 320 px; print CSS; post-print state restoration; no-JavaScript reading; and absence of browser/console errors or external requests. Tables may scroll inside their containers on narrow displays; the overall body did not overflow those tested viewports.

The report is static content with optional inline JavaScript. Browser checks observed **zero external network requests**, zero page errors, and zero console errors. An explicit user click on an external source link may open that source.

Print testing covered CSS visibility/layout and beforeprint/afterprint state, **not an exported PDF's pagination or visual inspection**. Safari, Firefox, physical printing, Windows host applications, accessibility screen-reader testing, and deployed hosting were not exercised.

## v1.0.0 migration

The original conversation-supplied `venture-evaluator-kit.zip` was extracted separately and its installer used with an isolated home directory. The new installer correctly refused to replace the differing version without `--replace`. With `--replace`, both host installations became version 1.1.0; each previous 1.0.0 manifest and exact SKILL.md were retained under skill-backups. A separate project's sentinel context file remained unchanged. The installed 1.1.0 renderer generated HTML and the installation's integrity still passed afterward.

See `test-results/migration-test-results.json`. This is a filesystem migration test, not a login or runtime test of Claude or Codex.

## Shipping artifact checks

After packaging, the release kit was extracted into another temporary directory. Its archive and SHA-256 inventory were checked, then its own installer, integrity checker, JSON validator, and report renderer were executed. The standalone skill ZIP was compared file-for-file to the kit's skill folder. Both archives were checked for unintended paths, caches, font binaries, and private example data.

See `test-results/release-check.json` for the exact checks. Hashes in SHA256SUMS cover every shipped file except the hash inventory itself. Repacking changes ZIP bytes but not the documented source/test results; the final archives are checked again after the release record is added.

## Not guaranteed by these tests

The host must actually load the skill and have access to user-supplied documents, a permitted file-writing tool, and Python for the bundled renderer. This release did not access a user's Claude/Codex account, inspect private account logs, execute the model-level eval scenarios, or prove the financial conclusions an AI might produce. PDF/DOCX/PPTX parsing remains the host's responsibility. HTML reports and their JSON can contain sensitive business data; review before sharing.

## 1.1.1 addendum · 2026-09-21

Patch release. `render_report.py` pattern validation switched from `re.search` to `re.fullmatch` so that IDs with a trailing newline (`"E1\n"`) are rejected instead of producing broken in-report anchors. One regression test added; the combined standard-library suite is **51 / 51 passed** on macOS (Python 3.14). Browser checks were not re-run for this patch; the rendered HTML structure is unchanged apart from the version string.
