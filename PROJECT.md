# Project: Gurmeet Kaur London Opportunity Directory — Remediation & Polish

## Architecture
The application is a zero-dependency, ultra-responsive single-page recruitment intelligence platform and interactive GIS directory hosted on GitHub Pages, accompanied by an exhaustive Markdown application dossier and a comprehensive 4-tier automated test suite.

### Data Flow
1. **Data Source**: Embedded in `index.html` as `const JOBS` (JavaScript Array of 50 job objects, each conforming to an invariant schema, with `star_behaviors` arrays for `gov-01` through `gov-09`).
2. **Interactive UI**:
   - Filter toolbar with 6 category sectors (`museum`, `arts`, `tutor`, `school`, `policy`, `uni`) + `saved` shortlist, styled as a mobile horizontally scrollable chip bar (<110px total header height).
   - Reactive search input matching across title, org, summary, area, and `why_fit`, with map viewport preservation to eliminate zoom jitter.
   - Haversine distance slider (from Imperial Wharf SW6 2ZH) and bidirectional table column sorter (`From SW6 ↑/↓`, `Remuneration ↑/↓`).
   - Interactive Leaflet.js map with Esri World Light Gray Canvas basemap, bottom-left legal attribution, radial offset dispersion for co-located markers (Bloomsbury, Whitehall, Waterloo), and dashed transit polylines.
   - Fixed-layout data table (`table-layout: fixed; width: 100%;`) eliminating the 1,548px blowout, with mixed-case typography and multi-line readable job titles.
   - Interactive mobile slide-over bottom sheet on vacancy row tap, rendering full transit breakdown, fit rationale, and actions.
   - Focus modal rendering tailored cover letters, speculative outreach emails with clean mailto launchers, role details, and a dedicated 🏛️ Success Profiles (STAR) tab rendering 36 full-length behavioral statements.
3. **Application Dossier**: `gurmeet-london-application-pack.md` (50 verified opportunities, including 36 Civil Service STAR statements).
4. **Offline Mirror**: `/Users/arimurad/Desktop/gurmeet-london-jobs.html` maintained with 100% SHA-256 byte-for-byte fidelity.
5. **Testing Harness**: Modular Python `unittest` suite (`tests/run_tests.py`, Tiers 1–4, 27 tests) verifying structural schemas, network availability (HTTP 200), geodetic bounds, transit realism, markdown-DOM parity, UI DOM IDs, and production deployment.

## Feature Inventory
| # | Feature | Description | Milestone | Source |
|---|---------|-------------|-----------|--------|
| 1 | R1.1 Esri Light Gray Basemap | Replace unauthenticated CartoDB with Esri Canvas, maxZoom 19, maxNativeZoom 16 | M1 | Survey 2 |
| 2 | R1.2 Legal Map Attribution | Bottom-left Leaflet attribution control with Esri copyright | M1 | Survey 2 |
| 3 | R1.3 Radial Marker Dispersion | Zero-dependency radial offset for co-located markers (Bloomsbury, Whitehall, Waterloo) | M1 | Survey 2 |
| 4 | R1.4 Search Jitter Elimination | Preserve map pan/zoom during search keystrokes via renderAll(false, false) | M1 | Survey 2 |
| 5 | R2.1 Fixed Table Layout | table-layout: fixed; width: 100%; eliminate 1,548px blowout in 755px pane | M1 | Survey 1 |
| 6 | R2.2 Mixed-Case Typography | Scope text-transform: none on tbody th and Title Case on thead th | M1 | Survey 1 |
| 7 | R2.3 Multi-line Readable Titles | Remove rigid 280px truncation, enable wrapping with title tooltips | M1 | Survey 1 |
| 8 | R2.4 Unified Button Design Tokens | 4-tier token system with standard padding, transitions, and hover states | M1 | Survey 1 |
| 9 | R3.1 Mobile Header Compression | Header <110px on 375x812 via horizontally scrollable category chip bar | M1 | Survey 1 |
| 10 | R3.2 Mobile Bottom Drawer Sheet | Interactive slide-over sheet on vacancy row tap in mobile Ledger view | M1 | Survey 1 |
| 11 | R3.3 Mobile Modal Area Expansion | Full viewport modal, tight header, scrollable tab chips, reading width >320px | M1 | Survey 1 |
| 12 | R4.1 Accessible Heading | Visually hidden h1 (Gurmeet Kaur — London Opportunities Directory) | M1 | Survey 2 |
| 13 | R4.2 Global Focus-Visible | 2px solid ink outline with 2px offset across all interactive elements | M1 | Survey 2 |
| 14 | R4.3 Keydown Bubbling Isolation | event.stopPropagation() on child buttons to prevent Space destroying row focus | M1 | Survey 2 |
| 15 | R4.4 Modal Focus Trap & Restore | Tab trapping inside dialog, focus return to trigger button on close | M1 | Survey 2 |
| 16 | R4.5 Arrow Key Decoupling | Decouple ArrowLeft/Right from modal navigation when focusing text/inputs | M1 | Survey 2 |
| 17 | R4.6 Toast Live Region | role="status" and aria-live="polite" on #toastMessage | M1 | Survey 2 |
| 18 | R5.1 Civil Service STAR Tab | 🏛️ Success Profiles tab rendering 36 full-length statements with copy buttons | M1 | Survey 3 |
| 19 | R5.2 Search why_fit Indexing | Include j.why_fit in search haystack and update count-uni badge | M1 | Survey 3 |
| 20 | R5.3 Bidirectional Sorting | Ascending ⇄ Descending toggling on From SW6 and Remuneration | M1 | Survey 3 |
| 21 | R5.4 Clean Mailto Launcher | 1-click clipboard copy of email body + clean launcher (to/subject only) | M1 | Survey 3 |
| 22 | R5.5 Stale 41->50 Updates | Update 4 stale counter references in DOM and Markdown pack | M1 | Survey 3 |
| 23 | R5.6 URL Hash State Sync | Synchronize category and job selection with URL hash (#policy, #gov-01) | M1 | Survey 3 |
| 24 | R6.1 Desktop Mirror SHA-256 Parity | 100% byte-for-byte SHA-256 parity with /Users/arimurad/Desktop/gurmeet-london-jobs.html | M1 | Survey 3 |
| 25 | R6.2 Automated Test Suite Passing | All 27 automated tests in tests/run_tests.py PASS (Exit Code 0) | M1 | Survey 3 |

## Milestones
| # | Name | Scope | Dependencies | Status |
|---|------|-------|-------------|--------|
| 1 | Comprehensive Remediation & Parity | R1.1–R1.4, R2.1–R2.4, R3.1–R3.3, R4.1–R4.6, R5.1–R5.6, R6.1–R6.2 | Survey Phase | COMPLETED |

## Code Layout
- `index.html`: Main interactive web application, UI styling, Leaflet map logic, modal controllers, and `const JOBS` data array.
- `gurmeet-london-application-pack.md`: Markdown recruitment dossier with tailored letters, emails, and Civil Service Success Profiles for all 50 roles.
- `/Users/arimurad/Desktop/gurmeet-london-jobs.html`: Offline desktop mirror of `index.html`.
- `tests/`: Modular test suite (`run_tests.py`, Tiers 1–4).
