<div align="center">

# healthcare_startup

### 医学数据采集 · ChatGPT 医疗咨询服务 · WeChat Mini-Program

A **data-driven healthcare startup** — a robust, factory-pattern Python pipeline that collects public medical data (hospitals · departments · doctors · medicines · doctor–patient Q&A), combined with a **ChatGPT-backed WeChat mini-program** for medical consultation.

[![GitHub Pages](https://img.shields.io/badge/GitHub%20Pages-live-2ea44f?logo=githubpages&logoColor=white)](https://1998x-stack.github.io/healthcare_startup/)
[![Deploy (Pages) — status](https://github.com/1998x-stack/healthcare_startup/actions/workflows/pages.yml/badge.svg)](https://github.com/1998x-stack/healthcare_startup/actions/workflows/pages.yml)
[![Python](https://img.shields.io/badge/Python-3.11%20%7C%203.12-informational?logo=python&logoColor=white)](https://www.python.org/)
[![Tests](https://img.shields.io/badge/tests-34%20passing-brightgreen)](tests/)

**Live demo site:** [https://1998x-stack.github.io/healthcare_startup/](https://1998x-stack.github.io/healthcare_startup/)

</div>

---

## Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Repository Structure](#repository-structure)
- [Getting Started](#getting-started)
- [Usage](#usage)
- [Dataset](#dataset)
- [Testing](#testing)
- [CI/CD & Deployment](#cicd--deployment)
- [Documentation](#documentation)
- [Roadmap](#roadmap)
- [Disclaimer](#disclaimer)

---

## Overview

`healthcare_startup` solves the problem of **finding the right hospital, department and
doctor for a patient's condition**, backed by a real public-data corpus. It has two tracks:

1. **Data acquisition (Python)** — three scrapers that collect and normalize public medical
   data from Chinese healthcare websites into reproducible, queryable JSON datasets.
2. **Smart consultation (WeChat mini-program)** — a ChatGPT-driven Mini Program that
   lets patients describe symptoms, ask questions, and get hospital/doctor recommendations.

The Python side was refactored around the **Factory design pattern** to eliminate heavy
duplication across the three scrapers while keeping each unit small, focused and testable.

## Key Features

- **Factory-pattern scraper framework** — `ScraperFactory.create(site)` returns a concrete
  scraper bound to its own parser. Adding a new data source = register one new parser.
- **Shared multiprocessing pipeline** — one `BaseScraper` owns worker orchestration via
  `multiprocessing.JoinableQueue`, fixing the legacy `cannot pickle '_thread.lock'` crash.
- **Offline-tested parsers** — field extraction is driven by an injected `fetch()`, so the
  entire test suite runs with **no network**.
- **Curated public datasets** — hospitals (18 districts, 223 entries), 738 medicines,
  department/doctor data for 北京协和医院, and ~6.7 MB of doctor–patient Q&A.
- **ChatGPT medical consultation** — `MedGPT/` mini-program with registration/login, Q&A,
  chat, hospital/doctor recommendation, and patient-profile management.
- **GitHub Pages** — a public data & architecture landing page, auto-deployed on every push.

---

## Architecture

The Python scrapers share a common flow — *build URL → fetch page → parse fields → save* —
so they are unified under one base class, with all site-specific extraction delegated to a
parser chosen by the factory.

```text
ScraperFactory.create('hospital')
        │
        ▼
┌───────────────────────────────────┐
│   HospitalScraper (BaseScraper)   │   build_tasks() → (key, url)
└───────────────┬───────────────────┘
                │  run() — multiprocessing.JoinableQueue
                ▼
          _worker (module-level, picklable)
                │  parser.parse(soup, url, fetch, logger)
                ▼
   HospitalParser │ MedicineParser │ QAParser
                │
                ▼
        result_queue → aggregate <site>.json
```

Full design rationale (including the `_thread.lock` fix) lives in
[`docs/architecture.md`](docs/architecture.md).

---

## Tech Stack

- **Language:** Python 3.8+ (used with 3.11/3.12)
- **Web scraping:** `requests`, `fake-useragent`, `beautifulsoup4`, `lxml`, `html5lib`
- **Data:** `pandas`, `numpy`, `tqdm`
- **Concurrency:** `multiprocessing` (`JoinableQueue`)
- **Mini-program:** WeChat Mini-Program (`MedGPT/`) + cloud functions
- **Docs/QA:** `pytest` for offline tests; `python-docx` for the architecture documents

---

## Repository Structure

```
healthcare_startup
├── scrapers/                 # Factory-pattern scraper package
│   ├── __init__.py           # create_scraper / ScraperFactory
│   ├── base.py               # BaseScraper — shared pipeline + multiprocessing
│   ├── parsers.py            # Hospital / Medicine / QA parsers + registry
│   ├── scrapers.py           # HospitalScraper / MedicineScraper / QAScraper
│   ├── factory.py            # ScraperFactory.create(site)
│   └── urls.py               # per-site URL builders
├── libs/
│   ├── utils.py              # get_soup / save_js / save_csv (logger optional)
│   ├── log.py                # logging system
│   └── tools/correct_name.py # mojibake-repair tool (--dry-run safe)
├── config.py                 # central configuration
├── run.py                    # CLI entrypoint
├── MedGPT/                   # WeChat mini-program (pages + cloud functions)
├── docs/                     # architecture & project docs
├── site/                     # GitHub Pages landing page
├── data/                     # scraped output datasets
└── tests/                    # offline pytest suite
```

---

## Getting Started

### Prerequisites

- Python 3.8+
- [Miniconda/Anaconda](https://docs.conda.io/) (recommended) or `venv`

### Install

```bash
conda create -n health python=3.11
conda activate health
pip install -r requirement.txt
```

Or with a plain virtual environment:

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirement.txt
```

---

## Usage

All three scrapers are driven by the factory through a single CLI:

```bash
# Scrape Beijing hospital / department / doctor data
python run.py hospital [--processes 8]

# Scrape medicine data (default 100,000 pages)
python run.py medicine [--processes 8] [--count 100000]

# Scrape doctor–patient Q&A (default 1,000 list pages)
python run.py qa [--processes 8] [--count 1000]
```

Programmatic use:

```python
from scrapers import create_scraper

scraper = create_scraper('medicine', num_processes=4, count=100)
result = scraper.run()          # dict of parsed records
print(len(result))              # records collected
```

---

## Dataset

Outputs are written to `config.SAVE_FOLDERS[site]` as `<site>.json`.

| site | scraper / parser | output path | content |
|------|------------------|-------------|---------|
| `hospital` | `HospitalScraper` / `HospitalParser` | `data/hospital/` | 北京 18 区县 · 223 家医院 · 科室 + 医生 |
| `medicine` | `MedicineScraper` / `MedicineParser` | `data/medician/` | 738 条：功能主治 / 参考价 / 说明书 / 相关药品 |
| `qa`       | `QAScraper` / `QAParser`             | `data/ques_ans.js` | 医生与患者问答语料（≈6.7 MB） |

The Beijing hospital seed list ships as `yiyuandiqu-beijing.csv` and `beijing_hospital.json`.

> Data is collected from **public medical websites** and organized for research/education.
> See the [Disclaimer](#disclaimer) section.

---

## Testing

```bash
pytest tests/ -v
```

The suite runs **fully offline** (injected fixture fetches, no real network):

- `test_factory.py` — `ScraperFactory.create()` resolution
- `test_base.py` — `BaseScraper` pipeline & config defaults
- `test_parsers.py` — field extraction for hospital / medicine / QA
- `test_urls.py` — URL builders & querystring helpers
- `test_utils.py` / `test_correct_name.py` — save helpers & mojibake tool
- `test_cli.py` — CLI argument parsing

An end-to-end multiprocessing smoke test is available offline:

```bash
python scripts/smoke_integration.py
```

---

## CI/CD & Deployment

[`.github/workflows/pages.yml`](.github/workflows/pages.yml) deploys the static
[`site/`](site/) landing page to **GitHub Pages**:

- Triggered **on every push to `main`** (or manually via *Actions → Deploy GitHub Pages*).
- High-assurance deployment with `contents: read`, `pages: write`, `id-token: write`.
- Live at [https://1998x-stack.github.io/healthcare_startup/](https://1998x-stack.github.io/healthcare_startup/).

---

## Documentation

| Document | Description |
|----------|-------------|
| [`docs/architecture.md`](docs/architecture.md) | Factory-pattern design & multiprocessing pipeline |
| [`docs/README.md`](docs/README.md) | Docs index |
| [`MedGPT.md`](MedGPT.md) | WeChat mini-program architecture |
| [`site/index.html`](site/index.html) | Public landing page |

---

## Roadmap

Prioritized goals from the original design (`MedGPT.md` / `README`):

- **P0** — Patient info archive (platform thinking), physical-exam-report interpretation, data flywheel.
- **P1** — Match user to the right hospital / department / doctor.
- **P2** — ChatGPT conversational Q&A with guidance & follow-up suggestions.
- **P3** — Answer-reliability scoring, generated exam reports, X-ray intake support.

---

## Disclaimer

- This project is for **research and educational purposes only**. It does **not** provide
  medical advice, diagnosis, or treatment.
- The dataset is aggregated from public medical websites and may contain errors; no
  guarantee of accuracy, completeness, or timeliness is made.
- The project is archived under **All Rights Reserved** (unless a LICENSE is added); please
  contact the author before reuse.

---

<div align="center"><sub>Built with ❤️ — data-driven, patient-first.</sub></div>