# Design: Reorganize `healthcare_startup` Codebase & Documentation

**Date:** 2026-08-18
**Status:** Approved for implementation planning

## 1. Goal

Deep-review, recheck, and reorganize the `healthcare_startup` codebase and
documentation with extreme detail, applying the **Factory design pattern** to the Python
code. Deliverables are threefold: **(1)** a clean Factory-pattern Python scraping package,
**(2)** a reorganized docs/README set, and **(3)** an updated `.docx` (existing) plus a new
architecture `.docx` (Chinese), both produced with the docx skill's render-and-QA workflow.

## 2. Scope & Out of Scope

**In scope**
- Refactor the 3 Python scrapers (`hospital_info.py`, `medician.py`, `ques_ans.py`) into
  a new `scrapers/` package using the Factory pattern with per-site parsers.
- Fix verified bugs (see §4).
- Remove duplicate/legacy files: `hospital_info_copy.py`, `medician_copy.py`, root `log.py`.
- Give empty `config.py` real content.
- Fix mojibake in mangled `data/` filenames using the corrected `correct_name` tool.
- Rewrite `README.md`, restructure `docs/`.
- Update existing DOCX `基于ChatGPT的患者信息管理与医疗服务优化.docx`.
- Produce new architecture DOCX `项目架构与技术路线.docx`.
- Add parser unit tests against HTML fixtures (no live network in tests).

**Out of scope**
- The WeChat Mini Program (`MedGPT/`) JavaScript — reorganized only insofar as its docs
  (`MedGPT.md`) are cleaned up; no JS logic changes.
- Full database migration / new scrapers for new sites (the registry design permits future
  sites, but none are added in this pass).
- Live re-running the full scrapes (network scraping) as part of this reorganization.

## 3. Target Python Architecture (Factory Pattern)

New package `scrapers/` built on the existing `libs/`:

```
scrapers/
  __init__.py        # public API: create_scraper(), SCRAPER_REGISTRY
  base.py            # BaseScraper (abstract) — shared pipeline + multiprocessing runner
  parsers.py         # BaseParser ABC + HospitalParser, MedicineParser, QAParser + PARSER_REGISTRY
  scrapers.py        # HospitalScraper, MedicineScraper, QAScraper (each binds one parser)
  factory.py         # ScraperFactory.create(site) -> concrete scraper
  urls.py            # per-site URL builders (xywy_hospital, wksc_medicine, xywy_qa)
```

### 3.1 `BaseScraper` (abstract)
- `__init__(site, parser, save_folder, num_processes, logger=None)`.
- Defines the shared pipeline that all scrapers inherit:
  - `build_tasks()` -> iterable of (label, url) tuples (abstract).
  - `parse(url) -> dict|None` — delegates to the bound parser (site-agnostic).
  - `run()` — orchestrates: build task queue -> spawn N workers -> collect -> save aggregate -> cleanup.
  - `_worker(...)` — module-level function that receives serializable args only
    (url, parser name, save_folder); creates its own `Log` internally; never pickles the
    logger or queue locks.
- Uses `multiprocessing.JoinableQueue` (NOT `queue.Queue`) to avoid the
  `cannot pickle '_thread.lock'` crash.
- Saves aggregate JSON via `libs/utils.save_js`.

### 3.2 Parsers (`parsers.py`)
- `BaseParser`: ABC with `name()` and `parse(soup, logger) -> dict`.
- `HospitalParser` — hospital/department/doctor extraction (from `hospital_info.py` logic).
- `MedicineParser` — drug/care/price/instructions (from `medician.py` logic).
- `PARSER_REGISTRY = {"hospital": HospitalParser, "medicine": MedicineParser, "qa": QAParser}`.

### 3.3 Concrete scrapers (`scrapers.py`)
- `HospitalScraper(BaseScraper)` binds `HospitalParser`.
- `MedicineScraper(BaseScraper)` binds `MedicineParser`.
- `QAScraper(BaseScraper)` binds `QAParser`.
- Each implements only its own `build_tasks()` and URL scheme.

### 3.4 Factory (`factory.py`)
- `ScraperFactory.create(site, **kwargs)` resolves `site` against a registry
  `{site_name: (scraper_cls, parser_cls)}`, constructs the scraper, returns it.
- `scrapers/__init__.py` exports `create_scraper = ScraperFactory.create`.

### 3.5 URL builders (`urls.py`)
- `hospital_urls`, `medicine_urls`, `qa_urls` — pure functions producing seed URLs /
  querystring helpers (port `add_page_querystring`, `replace_url_path`, `get_link` here).

## 4. `libs/` refactor
- Keep `libs/utils.py`: `get_soup`, `save_csv`, and `save_js` (keep the name to minimize churn)
  with `logger` made **optional**, defaulting to a no-op — fixing the required-arg bug.
- Keep `libs/log.py` (`Log` class) as the single logging source.
- Delete the duplicate root `log.py`.
- Move `correct_name.py` into `libs/` (or keep at root as `tools/fix_mojibake.py`) — used
  once to repair mangled `data/` names, then kept as a utility.

### 5. `config.py`
- Central config: `SAVE_ROOT`, per-site save subfolders, `DEFAULT_NUM_PROCESSES`,
  `SITE_NAMES`, seed-data file paths, parser/scraper strings for the factory.
- Scrapers read paths from config rather than hardcoding `'./data/...'`.

## 6. Data repair
- Use the corrected `correct_name` utility to fix mojibake filenames/dir names under
  `data/` (the `renamed-?»` prefixed entries) so they resolve to proper UTF-8 names.
- No schema changes to JSON content; only filenames/keys corrected where clearly mojibake.

## 7. Documentation reorganization
- **`README.md`** rewritten as a clean index: overview, directory tree, install
  (`conda create -n health` + `pip install -r requirement.txt`), how to run each scraper
  via the factory, data output table, targets, cost assumptions, known issues/debug.
- **`docs/`** restructured:
  - `docs/README.md` — index of docs.
  - `docs/chatgpt-mini-program-design.md` — consolidated/cleaned content from
    `docs/CHAT_GPT_HELP_ME1.md` and `docs/CHAT_GPT_HELP_ME2.markdown` (prompt history +
    mini-program architecture). Originals archived to `docs/archive/`.
  - `docs/architecture.md` — Factory-pattern Python architecture explanation &
    class/parser/multiprocessing flow.
  - Old `docs/CHAT_GPT_HELP_ME1.md` / `CHAT_GPT_HELP_ME2.markdown` moved to `docs/archive/`.
- **`MedGPT.md`** kept as the mini-program architecture doc, lightly cleaned.

## 8. Bug fixes (from self-review, verified)
1. `hospital_info.py` used threading `Queue` (`from queue import Queue`) with
   multiprocessing → `cannot pickle '_thread.lock'`. Fix: `multiprocessing.JoinableQueue`.
2. `libs/utils.save_js` required `logger` positional but callers omitted it →
   make `logger` optional.
3. `medician_copy.py` line 26 `save_js(js, ...)` used undefined `js` (→ `NameError`);
   resolved by removing the duplicate (the good `medician.py` logic becomes `MedicineScraper`).
   (`medician.py`'s own aggregate call at line 79 is correct — `js = {}` is defined in `main()`.)

## Test / verification approach
- `tests/test_factory.py` — `create_scraper("hospital")` returns the right instance/parser.
- `tests/test_parsers.py` — each parser against saved HTML fixtures (from `data/`), no
  network.
- `tests/test_url.py` — URL builders + querystring helpers.
- Verify no imports of removed files; `python -c "from scrapers import create_scraper"`.

## 9. Completion checklist
- [ ] `scrapers/` package present; factory + parsers + base + concrete scrapers + urls.
- [ ] `libs/` refactored; root `log.py`, `_copy.py` removed.
- [ ] `config.py` populated and used.
- [ ] `data/` mojibake names fixed.
- [ ] `README.md` + `docs/` reorganized (archives in place).
- [ ] Existing DOCX updated + new architecture DOCX produced (render + QA pass).
- [ ] Tests pass.

## Canvas of naming/decisions taken
- DOCX new file: `项目架构与技术路线.docx`; existing filename kept, content updated.
- Duplicates removed: `hospital_info_copy.py`, `medician_copy.py`, root `log.py`.
- `data/` mojibake fixed.