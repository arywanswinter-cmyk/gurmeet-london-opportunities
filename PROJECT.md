# Project: Gurmeet Kaur London Opportunity Directory — 6-Pillar Active Employment Engine

## Architecture
The application is a lightweight, zero-dependency, ultra-responsive single-page recruitment intelligence platform and interactive GIS directory hosted on GitHub Pages, accompanied by an exhaustive Markdown application dossier and a comprehensive 4-tier automated test suite.

### Data Flow
1. **Data Source**: Embedded in `index.html` as `const JOBS` (JavaScript Array of 50 job objects, each conforming to an invariant 23-key schema).
2. **Interactive UI**:
   - Filter toolbar with 6 category sectors (`museum`, `arts`, `tutor`, `school`, `policy`, `uni`) + `saved` shortlist.
   - Reactive search input matching across title, org, summary, area, and why_fit.
   - Haversine distance slider (from Imperial Wharf SW6 2ZH) and salary/commute sorter.
   - Interactive Leaflet.js map with custom SVG/divIcon pins, tooltips, and dashed transit polylines.
   - Focus modal rendering tailored cover letters, speculative outreach emails, role details, and one-click copy tools.
3. **Application Dossier**: `gurmeet-london-application-pack.md` divided into 6 parts (49 live vacancies + 1 Gallery 44 Easter Egg). Contains metadata, formatted outreach emails, tailored cover letters / personal statements, and Civil Service Success Profiles STAR behaviors.
4. **Offline Mirror**: `/Users/arimurad/Desktop/gurmeet-london-jobs.html` and `/Users/arimurad/Desktop/gurmeet-london-application-pack.md` maintained with byte-for-byte fidelity.
5. **Testing Harness**: Modular Python `unittest` suite (`tests/run_tests.py`, Tiers 1–4) validating structural schemas, network availability (HTTP 200), geodetic bounds, transit realism, markdown-DOM parity, UI DOM IDs, and production deployment.

## Code Layout
- `index.html`: Main interactive web application, UI styling, Leaflet map logic, modal controllers, and `const JOBS` data array.
- `gurmeet-london-application-pack.md`: Markdown recruitment dossier with tailored letters, emails, and Civil Service Success Profiles for all 50 roles.
- `/Users/arimurad/Desktop/gurmeet-london-jobs.html`: Offline desktop mirror of `index.html`.
- `/Users/arimurad/Desktop/gurmeet-london-application-pack.md`: Offline desktop mirror of the application pack.
- `tests/`:
  - `run_tests.py`: CLI test harness runner and reporter.
  - `test_utils.py`: Parser utilities, constants, Haversine formula, and HTTP 200 concurrent checker.
  - `test_tier1_features.py`: Verifies total job count (50), 6-sector distribution (8/8/8/8/9/9), deep-link reachability (HTTP 200), and deadlines.
  - `test_tier2_boundaries.py`: Geodetic boundary bounds, UK postcodes, transit string syntax, letter/email character lengths, and formatting.
  - `test_tier3_cross_features.py`: Haversine formula compliance (<0.25 mi tolerance), modal-to-pack character-for-character parity, counter badges, ID schemas.
  - `test_tier4_scenarios.py`: Search queries, distance thresholds, sort order simulations, git origin, and live GitHub Pages verification.

## 6 Sectors Breakdown (50 Total Vacancies)
1. **Curator & Museum (`museum`)**: 8 live vacancies (e.g. V&A, British Museum, Science Museum, Museum of London, Leighton House, Imperial War Museum, Design Museum, Wallace Collection).
2. **Literature & Arts (`arts`)**: 8 live vacancies (e.g. Southbank Centre, Royal Society of Literature, Barbican, Somerset House, Poetry Society, PEN International, British Library, ICA).
3. **West London Schools (`school`)**: 8 live vacancies (e.g. Lady Margaret School, Fulham Boys School, Chelsea Academy, West London Free School, Godolphin & Latymer, St Paul's Girls', Latymer Upper, Holland Park).
4. **Education & Access (`tutor`)**: 8 live vacancies (e.g. The Brilliant Club, IntoUniversity, Access Project, CoachBright, Tutor Trust, Universify, Sutton Trust, Debate Mate).
5. **Civil Service & Policy (`policy`)**: 9 opportunities (8 live vacancies at FCDO, British Council, DCMS, National Archives, Historic England, GLA City Hall, DfE + 1 Gallery 44 Primrose Hill Easter Egg).
6. **Universities & Research Institutes (`uni`)**: 9 live vacancies (LSE, King's College London, UCL, SOAS, The British Academy, Paul Mellon Centre for Studies in British Art, QMUL, Birkbeck, Institute of Historical Research).
