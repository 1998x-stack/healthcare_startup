# Reorganize `healthcare_startup` Codebase & Docs — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Refactor the 3 Python scrapers into a Factory-pattern `scrapers/` package, fix verified bugs, remove duplicate/legacy files, reorganize docs, and deliver updated + new Chinese `.docx` files (docx skill render-and-QA).

**Architecture:** A `ScraperFactory.create(site)` returns a concrete scraper (`BaseScraper` subclass) already bound to its per-site parser (`BaseParser` subclass). `BaseScraper` owns the shared multiprocessing pipeline (`multiprocessing.JoinableQueue` + module-level picklable worker) and delegates all field extraction to the parser. Parsers support an injected `fetch(soup)` callable so unit tests run without network.

**Tech Stack:** Python 3.11, requests + fake_useragent + BeautifulSoup, multiprocessing, pandas, pytest, python-docx.

## Global Constraints
- Python scrapers live under a new `scrapers/` package; shared helpers stay in `libs/`.
- Use `multiprocessing.JoinableQueue`, never `queue.Queue` (fixes `_thread.lock` crash).
- `libs/utils.save_js` must work with `logger=None` (silent no-op logger).
- Keep `save_js` name (do not rename to `save_json`).
- Delete duplicates: root `log.py`, `hospital_info_copy.py`, `medician_copy.py`.
- Populate `config.py` and have scrapers read paths from it (no hardcoded `./data/...`).
- Tests run with **no network** — inject a fake `fetch`.
- Commits in focused TDD units; each task ends testable and committed.
- Docs: rewrite root `README.md`; restructure `docs/` (archive old `CHAT_GPT_HELP_ME*.md`); keep `MedGPT.md`.
- DOCX language: Chinese. Output filename kept for existing doc; new doc = `项目架构与技术路线.docx`.
- Data mojibake filenames fixed once via corrected name tool (documented in Task 8).

Architecture decision (from spec §3.4): factory resolves `{site: (scraper_cls, parser_cls)}`; scraper is 1:1 bound to a parser; adding a site later = register new parser, no new scraper class.

---

### Task 1: `libs/utils.py` — make logger optional & add URL helpers as module utilities

**Files:**
- Modify: `libs/utils.py`
- Modify: `config.py`
- Test: `tests/test_utils.py`

**Interfaces:**
- Consumes: nothing (replaces current utils).
- Produces: `save_js(js, logger=None, save_folder='./data/', file_name='jibinginfo.json', exists_ok=False)`, `save_csv`, `get_soup(url, logger=None, timeout=10)`, module-level `_noop`, `silent_logger()`. Also `config.py` constants used by later tasks.

- [ ] **Step 1: Make `save_js` and `get_soup` tolerate `logger=None`**

```python
# libs/utils.py (replace body of save_js/get_soup and add helpers)
import json, os, csv, time, random, codecs
import requests
from requests.exceptions import RequestException, Timeout
from fake_useragent import UserAgent
from bs4 import BeautifulSoup


def _noop(*args, **kwargs):
    return None


class _SilentLogger:
    log_info = staticmethod(_noop)
    log_exception = staticmethod(_noop)


def silent_logger():
    return _SilentLogger()


def save_js(js, logger=None, save_folder='./data/', file_name='jibinginfo.json', exists_ok=False):
    if logger is None:
        logger = silent_logger()
    if not os.path.exists(save_folder):
        os.makedirs(save_folder)
    for char in ['\\', '/', ':', '*', '?', '"', '<', '>', '|']:
        file_name = file_name.replace(char, '')
    save_path = os.path.join(save_folder, file_name)
    try:
        if exists_ok and os.path.exists(save_path):
            with codecs.open(save_path, 'a', encoding='utf-8') as f:
                json.dump(things, f, ensure_ascii=False, indent=4)
        else:
            with codecs.open(save_path, 'w', encoding='utf-8') as f:
                json.dump(things, f, ensure_ascii=False, indent=4)
        logger.log_info(f'JSON got {file_name} saved to {save_path}')
    except Exception as e:
        print(f'save error {file_name}: {e}')
        logger.log_exception()


def get_soup(url, logger=None, timeout=15):
    if logger is None:
        logger = silent_logger()
    ua = UserAgent()
    headers = {'User-Agent': ua.random}
    time.sleep(random.uniform(0.5, 1.5))
    try:
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()
    except (RequestException, Timeout):
        logger.log_exception(f'{url} status {getattr(response, "status_code", None)}')
        return None
    try:
        return BeautifulSoup(response.content, 'html.parser', from_encoding='utf-8')
    except AttributeError:
        logger.log_exception('Response content attribute error')
        return None
```

Also add matching `import codecs` and `def save_csv(data, logger=None, save_folder=...)` kept as-is but with the same optional-logger guard.

- [ ] **Step 2: Write failing test `tests/test_utils.py`**

```python
import os
import tempfile
from libs.utils import save_js, silent_logger


def test_save_js_with_no_logger():
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, 'sub', 'x.json')
        save_js({'a': 1}, save_folder=os.path.dirname(p), file_name='x.json')
        assert os.path.exists(p)
```

- [ ] **Step 3: Run it** — create `tests/` then:

```bash
pip install -q pytest
pytest tests/test_utils.py -v
```
Expected: FAIL (regression from old `save_js(js, logger, ...)` that raised on missing logger).

- [ ] **Step 4: Confirm it passes after Step 1 edit.**

Run `pytest tests/test_utils.py -v` → PASS.

- [ ] **Step 5: Create `config.py`** (replaces the empty file):

```python
import os

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
SAVE_ROOT = os.path.join(ROOT_DIR, 'data')
LOGS_ROOT = os.path.join(ROOT_DIR, 'logs')

DEFAULT_NUM_PROCESSES = 8
DEFAULT_PAGE_TIME = 120

SITE_NAMES = ('hospital', 'medicine', 'qa')

SAVE_FOLDERS = {
    'hospital': os.path.join(SAVE_ROOT, 'hospital'),
    'medicine': os.path.join(SAVE_ROOT, 'medician'),
    'qa': os.path.join(SAVE_ROOT, 'ques_ans'),
}

SEED_DATA = {
    'beijing_csv': os.path.join(ROOT_DIR, 'yiyuandiqu-beijing.csv'),
    'beijing_json': os.path.join(ROOT_DIR, 'beijing_hospital.json'),
}
```

- [ ] **Step 6: Commit**

```bash
git add libs/utils.py config.py tests/test_utils.py
git commit -m "feat: silent-logger get/save helpers, optional logger, config.py"
```

---

### Task 2: URL builders package (`scrapers/urls.py`)

**Files:**
- Create: `scrapers/urls.py`
- Test: `tests/test_urls.py`

**Interfaces:**
- Consumes: nothing beyond stdlib `re`.
- Produces: `add_page_querystring(url,page)`, `replace_url_path(url,old,new)`,
  `get_link(url)`, `medicine_urls(count=100000)`, `qa_urls(count=1000)`,
  `qa_prefix()`, `host_list_page_urls(count=1000)`.

- [ ] **Step 1: Write failing test `tests/test_urls.py`**

```python
from scrapers.urls import add_page_querystring, get_link, replace_url_path


def test_add_query_only_once():
    u = 'http://x/y.htm'
    u2 = add_page_querystring(u, 2)
    assert u2.endswith('?&page=2')
    assert add_page_querystring(u2, 3) == u2


def test_get_link():
    assert get_link('//a.com/p/q.htm') == 'http://a.com/p/q.htm'


def test_replace_path():
    base = 'http://a.com/yiyuankeshi-pumch-x.htm'
    out = replace_url_path(base, 'yiyuankeshi-pumch-', 'yiyuankeshimenzhenshijian-pumch-')
    assert 'yiyuankeshimenzhenshijian' in out
```

- [ ] **Step 2: Run to confirm `scrapers` import fails.** `pytest tests/test_urls.py -v` → ImportError.

- [ ] **Step 3: Create `scrapers/urls.py`**

```python
import re


def add_page_querystring(url, page_num):
    if re.search(r'(\?&page=\d+)$', url):
        return url
    return url + '?&page={}'.format(page_num)


def replace_url_path(url, old_path='yiyuankeshi-pumch-', new_path='yiyuankeshimenzhenshijian-pumch-'):
    pattern = re.compile(r'/('+re.escape(old_path)+r')')
    return re.sub(pattern, '/'+new_path, url)


def get_link(url):
    if not url:
        return None
    m = re.match(r'//(.*?)/(.*?)$', url)
    return f'http://{m.group(1)}/{m.group(2)}' if m else url


def medicine_urls(count=100000):
    return [f'http://y.wksc.com/goods/{i}.htm' for i in range(1, count + 1)]

QA_PREFIX = 'http://club.xyqyw.com'


def qa_list_page_urls(count=1000):
    return [f'http://club.xyqyw.com/list_all_{i}.htm' for i in range(1, count + 1)]
```

> Note about `replace_url_path`: the original substitution embedded the host like `pumch`; the helper above replaces the literal path segment. Keep it test-driven — if a real URL fails, fix in test, do not silently degrade.

- [ ] **Step 4: Run `pytest tests/test_urls.py -v` → PASS.**
- [ ] **Step 5: Commit**

```bash
git add scrapers/urls.py tests/test_urls.py
git commit -m "feat: URL builders for scrapers"
```

---

### Task 3: `BaseScraper` + module-level worker (`scrapers/base.py`)

**Files:**
- Create: `scrapers/__init__.py` (partial)
- Create: `scrapers/base.py`
- Test: `tests/test_base.py`

**Interfaces:**
- Consumes: Task 1 `config`, Task 2 urls, `libs.utils.save_js/get_soup`.
- Produces: `BaseScraper` (abstract): `site`, `__init__(save_folder=None, num_processes=None, fetch=None)`, `build_tasks()` abstract, `run() -> dict`, `save_aggregate(dict)`. Also module-level `_default_fetch(url)` and `_worker(...)` (picklable by reference).

- [ ] **Step 1: `scrapers/__init__.py`**

```python
from scrapers.factory import create_scraper, ScraperFactory

__all__ = ['create_scraper', 'ScraperFactory']
```

- [ ] **Step 2: Write failing test `tests/test_base.py`** (subclass + fake parser stub; run in a single process path so no spawn needed yet)

```python
import pytest
from scrapers.base import BaseScraper


class Dummy(BaseScraper):
    site = 'dummy'
    def build_tasks(self):
        return [('k1', 'http://example.com/1')]


def test_run_returns_aggregate(monkeypatch, tmp_path):
    class _FakeParser:
        class DummyParser:
            def parse(self, soup, fetch=None, logger=None):
                return {'k1': {'ok': True}}
    # shortest: run with num_processes=1, fake fetch reading tmp file
    s = Dummy(save_folder=str(tmp_path), num_processes=1, fetch=lambda u: None)
    out = s.run()
    assert isinstance(out, dict)
```

Note: with `num_processes=1` and `lambda fetch`, multiprocessing on macOS still spawns; keep the minimal test asserting `run()` returns a dict and that `build_tasks()` is captured — refine in implementation if the process does not spawn by using `multiprocessing.get_context('fork')` where possible.

- [ ] **Step 3: Implement `scrapers/base.py`**

```python
import abc
import os
from multiprocessing import JoinableQueue, Process

from libs.log import Log
from libs import utils
import config

def _worker(task_queue, result_queue, parser_name, fetch, logger, save_folder):
    from scrapers.parsers import PARSER_REGISTRY
    if fetch is None:
        fetch = utils.get_soup
    if logger is None:
        logger = Log(parser_name)
    parser = PARSER_REGISTRY[parser_name]()
    while True:
        task = task_queue.get()
        if task is None:
            task_queue.task_done()
            break
        key, url = task
        try:
            soup = fetch(url)
            if soup is not None:
                result = parser.parse(soup, fetch=fetch, logger=logger)
                if result and result.get('data'):
                    result_queue.put((key, result['data']))
        except Exception as err:
            logger.log_exception(str(err))
        finally:
            task_queue.task_done()


class BaseScraper(abc.ABC):
    site = 'base'

    def __init__(self, site=None, save_folder=None, num_processes=None, fetch=None, logger=None):
        self.site = site or self.site
        self.save_folder = save_folder or config.SAVE_FOLDERS.get(self.site, config.SAVE_ROOT)
        self.num_processes = num_processes or config.DEFAULT_NUM_PROCESSES
        self._fetch = fetch or utils.get_soup
        self.logger = logger or Log(self.site)

    @abc.abstractmethod
    def build_tasks(self):
        """yield (key, url) tuples"""

    def aggregate_name(self):
        return f'{self.site}.json'

    def run(self):
        task_queue = JoinableQueue()
        result_queue = JoinableQueue()
        for t in self.build_tasks():
            task_queue.put(t)
        for _ in range(self.num_processes):
            task_queue.put(None)

        procs = []
        for _ in range(self.num_processes):
            p = Process(target=_worker, args=(task_queue, result_queue, self.site, self._fetch, self.logger, self.save_folder))
            p.daemon = True
            p.start()
            procs.append(p)

        task_queue.join()
        aggregate = {}
        while not result_queue.empty():
            key, data = result_queue.get()
            aggregate[key] = data
        for p in procs:
            p.terminate(); p.join()

        self.save_aggregate(aggregate)
        return aggregate

    def save_aggregate(self, aggregate):
        utils.save_js(aggregate, logger=self.logger, save_folder=self.save_folder, file_name=self.aggregate_name())
```

(Trim helpers at bottom: `def aggregate_name(self): return f'{self.site}.json'`; also `_picklable_fetch= getattr(utils,'get_soup')`.)

- [ ] **Step 4: Run `pytest tests/test_base.py -v` → PASS** (if `_worker` imports `scrapers.parsers` which isn't in place yet, guard the test to only assert `build_tasks()`; move the full `run()` smoke test into Task 6).

- [ ] **Step 5: Commit**

```bash
git add scrapers/__init__.py scrapers/base.py tests/test_base.py
git commit -m "feat: BaseScraper pipeline + picklable worker"
```

---

### Task 4: Parsers (`scrapers/parsers.py`) + fixture-driven tests

**Files:**
- Create: `scrapers/parsers.py`
- Create: `tests/fixtures/medicine.html`, `tests/fixtures/qa.html`
- Test: `tests/test_parsers.py`

**Interfaces:**
- Consumes: Task 3 base (uses `fetch` in `parse`).
- Produces: `BaseParser(name, parse(soup, fetch=None, logger=None) -> dict)`; concrete `MedicineParser`, `QAParser`, `HospitalParser(stub may nest)`. `PARSER_REGISTRY = {'hospital': HospitalParser, 'medicine': MedicineParser, 'qa': QAParser}`.

- [ ] **Step 1: Write failing test `tests/test_parsers.py`** (medicine parser extracts fields from fixture)

```python
from bs4 import BeautifulSoup
from scrapers.parsers import MedicineParser


def _load(name):
    with open(f'tests/fixtures/{name}.html', encoding='utf-8') as f:
        return BeautifulSoup(f.read(), 'html.parser')


def test_medicine_extracts():
    soup = _load('medicine')
    data = MedicineParser().parse(soup)
    assert '药品名称' in data
    assert '功能主治' in data
```

- [ ] **Step 2: Create a minimal `tests/fixtures/medicine.html`**

```html
<!doctype html>
<html><head><meta charset="utf-8"></head><body>
<div class="yao-name">测试药片</div>
<div class="ml20"><dd>治标</dd></div>
<div class="js-price-red">9.9</div>
<div id="pTop"><dt>规格</dt><dd>0.25g</dd><p>说明文字</p></div>
<div class="xg-yao-name">相关药A</div>
</body></html>
```

- [ ] **Step 3: Implement `MedicineParser`**

```python
import abc


class BaseParser(abc.ABC):
    name = 'base'

    @abc.abstractmethod
    def parse(self, soup, fetch=None, logger=None):
        raise NotImplementedError


class MedicineParser(BaseParser):
    name = 'medicine'

    def parse(self, soup, fetch=None, logger=None):
        data = {
            '药品名称': soup.select_one('.yao-name').text.strip() if soup.select_one('.yao-name') else '',
            '功能主治': soup.select_one('.ml20 dd').text.strip() if soup.select_one('.ml20 dd') else '',
            '参考价格': soup.select_one('.js-price-red').text.strip() if soup.select_one('.js-price-red') else '',
            '商品介绍': {a.text.strip(): b.text.strip() for a, b in zip(soup.select('#pTop dt'), soup.select('#pTop dd'))},
            '说明书': '\n'.join(p.text.strip() for p in soup.select('#pTop p')),
            '相关药品': [a.text.strip() for a in soup.select('.xg-yao-name')],
        }
        return {'key': soup.select_one('.yao-name').text.strip() if soup.select_one('.yao-name') else '', 'data': data}
```

- [ ] **Step 4: Add `HospitalParser` (port of hospital_info extraction) and `QAParser` (port of ques_ans extraction)** — port the field logic from `hospital_info.py` and `ques_ans.py` into these two classes, keeping each `parse(soup, fetch=..., logger=...)` self-contained. (See source files lines referenced in the spec §3.2.)

- [ ] **Step 5: Register**

```python
PARSER_REGISTRY = {
    'hospital': HospitalParser,
    'medicine': MedicineParser,
    'qa': QAParser,
}
```

- [ ] **Step 6: Run `pytest tests/test_parsers.py -v` → PASS.**
- [ ] **Step 7: Commit.**

---

### Task 5: Concrete scrapers + factory (`scrapers/scrapers.py`, `scrapers/factory.py`)

**Files:**
- Create: `scrapers/scrapers.py`, `scrapers/factory.py`
- Test: `tests/test_factory.py`

**Interfaces:**
- Consumes: Task 3 `BaseScraper`, Task 4 `PARSER_REGISTRY`, Task 2 urls.
- Produces: `HospitalScraper`, `MedicineScraper`, `QAScraper`; `ScraperFactory.create(site, **kw)`.

- [ ] **Step 1: Failing test `tests/test_factory.py`**

```python
from scrapers import create_scraper


def test_factory_returns_hospital():
    s = create_scraper('hospital')
    assert s.__class__.__name__ == 'HospitalScraper'
    assert s.parser.name == 'hospital'


def test_factory_unknown_raises():
    import pytest
    with pytest.raises(ValueError):
        create_scraper('nope')
```

- [ ] **Step 2: Implement `factory.py`**

```python
from scrapers.scrapers import HospitalScraper, MedicineScraper, QAScraper

SCRAPER_REGISTRY = {
    'hospital': HospitalScraper,
    'medicine': MedicineScraper,
    'qa': QAScraper,
}


class ScraperFactory:
    def create(self, site, **kwargs):
        if site not in SCRAPER_REGISTRY:
            raise ValueError(f'Unknown site: {site}')
        return SCRAPER_REGISTRY[site](site=site, **kwargs)


create_scraper = ScraperFactory().create
```

- [ ] **Step 3: Implement `scrapers.py`** — three thin `BaseScraper` subclasses; each sets `site`, sets `self.parser = PARSERPARSER_REGISTRY[site]()`, and `build_tasks()` via urls helper.

```python
from scrapers.base import BaseScraper
from scrapers.parsers import PARSER_REGISTRY
from scrapers import urls


class HospitalScraper(BaseScraper):
    site = 'hospital'
    def __init__(self, site='hospital', **kw):
        super().__init__(site=site, **kw)
        self.parser = PARSER_REGISTRY['hospital']()
    def build_tasks(self):
        # from beijing_hospital.json -> per-hospital (label, url)
        import json, config
        with open(config.SEED_DATA['beijing_json'], encoding='utf-8') as f:
            beijing = json.load(f)
        for location, hos in beijing.items():
            for hurl, hname in zip(hos.get('hospital_url', []), hos.get('hospital_name', [])):
                yield (f'{location}/{hname}', hurl)


class MedicineScraper(BaseScraper):
    site = 'medicine'
    def __init__(self, site='medicine', count=100000, **kw):
        super().__init__(site=site, **kw)
        self.parser = PARSER_REGISTRY['medicine']()
        self.count = count
    def build_tasks(self):
        for url in urls.medicine_urls(self.count):
            yield (url, url)


class QAScraper(BaseScraper):
    site = 'qa'
    def __init__(self, site='qa', count=1000, **kw):
        super().__init__(site=site, **kw)
        self.parser = PARSER_REGISTRY['qa']()
        self.count = count
    def build_tasks(self):
        for url in urls.qa_urls(self.count):
            yield (url, url)
```

- [ ] **Step 4: Run `pytest tests/test_factory.py` → PASS** and `python -c "from scrapers import create_scraper; print(create_scraper('medicine'))"`.
- [ ] **Step 5: Commit.**

---

### Task 6: CLI entrypoint `run.py` + end-to-end smoke

**Files:**
- Create: `run.py`
- Test: `tests/test_cli.py` (arg validation only)

**Interfaces:**
- Consumes: `config`, `scrapers/{factory,base,parsers}`.
- Produces: `python run.py hospital|medicine|qa [--processes N] [--count N]`.

- [ ] **Step 1: `run.py`**

```python
import argparse
from scrapers import create_scraper
from libs.log import Log
import config


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('site', choices=config.SITE_NAMES)
    ap.add_argument('--processes', type=int, default=config.DEFAULT_NUM_PROCESSES)
    ap.add_argument('--count', type=int, default=None)
    args = ap.parse_args()
    logger = Log(args.site)
    kw = {'num_processes': args.processes}
    if args.count:
        kw['count'] = args.count
    scraper = create_scraper(args.site, **kw, logger=logger)
    result = scraper.run()
    logger.log_info(f'[{args.site}] collected {len(result)}')


if __name__ == '__main__':
    main()
```

Note: update `BaseScraper.__init__` to accept `logger=None` if not already; adjust `create_scraper(**kw, logger=logger)` accordingly.

- [ ] **Step 1: Update `run.py` to pass `logger` into the factory (BaseScraper already accepts `logger=`)**, then:

```bash
python run.py --help
pytest tests/test_cli.py -v
```
Expected: PASS (validates the `hospital|medicine|qa` choices).
- [ ] **Step 3: Commit.**

---

### Task 7: Cleanup — remove duplicates, move `correct_name`

**Files:**
- Delete: `hospital_info_copy.py`, `medician_copy.py`, `log.py` (root)
- Move: `correct_name.py` → `libs/tools/correct_name.py`
- Modify: nothing else

- [ ] **Step 1: Delete duplicate/legacy files.**

```bash
git rm hospital_info_copy.py medician_copy.py log.py
git mv correct_name.py libs/tools/correct_name.py
```

- [ ] **Step 2: Verify no orphan references.**

```bash
grep -rn "hospital_info_copy\|medician_copy\|from log import\|import log" --include=*.py . | grep -v "__pycache__" || echo "clean"
```

- [ ] **Step 3: Commit.**

```bash
git add -A
git commit -m "refactor: remove duplicated/legacy scraper files; move correct_name into tools"
```

---

### Task 8: Fix `data/` mojibake names

**Files:**
- Run: `libs/tools/correct_name.py`

- [ ] **Step 1: Run the tool against `data/`.**

```bash
python libs/tools/correct_name.py
```

Expected: mojibake files (e.g. `renamed-»ù±¾Íâ¿Æ`) renamed to proper UTF-8 (`基本外科`). If tool errors, debug per `systematic-debugging` skill; do not manually mass-rename.

- [ ] **Step 2: Spot-check a few renamed files print correctly.**

```bash
ls data/hospital/东城/北京协和医院/ | head
```

- [ ] **Step 3: Commit the data name fixes.**

```bash
git add -A
git commit -m "fix: correct mojibake filenames under data/"
```

---

### Task 9: Docs reorganization

**Files:**
- Rewrite: `README.md`
- Create: `docs/README.md`, `docs/architecture.md`, `docs/archive/`
- Move: `docs/CHAT_GPT_HELP_ME1.md`, `docs/CHAT_GPT_HELP_ME2.markdown` → `docs/archive/`

- [ ] **Step 1: Rewrite `README.md`** — overview, directory tree, install (`conda create -n health` + `pip install -r requirement.txt`), run instructions (`python run.py hospital|medicine|qa`), data output table, targets, cost, known issues/debug. Keep original URL list under a "数据源" section.
- [ ] **Step 2: Create `docs/README.md`** (index) and `docs/architecture.md` (Factory-pattern architecture + class/parser/multiprocessing flow text + mermaid flowchart).
- [ ] **Step 3: Move the two design-historpy markdown files into `docs/archive/`.**

```bash
mkdir -p docs/archive docs/tmp
git mv docs/CHAT_GPT_HELP_ME1.md docs/archive/
git mv docs/CHAT_GPT_HELP_ME2.markdown docs/archive/CHAT_GPT_HELP_ME2.md
```

- [ ] **Step 4: Commit.**

```bash
git add -A
git commit -m "docs: reorganize README and docs/ (index + architecture), archive originals"
```

---

### Task 10: DOCX deliverables (docx skill render + QA)

**Files:**
- Modify: `基于ChatGPT的患者信息管理与医疗服务优化.docx` (update content to reflect new architecture)
- Create: `项目架构与技术方案.docx`

Refer to the **python + docx** skills before coding the generator script. Use `render_docx.py` to render pages, inspect PNGs, iterate until layout is flawless, then export.

- [ ] **Step 1: Read docx skill (`/Users/x/.pi/agent/skills/pdfs/SKILL.md` for render workflow; docx skill for python-docx API) and inspect the existing DOCX content via python-docx.**
- [ ] **Step 2: Write a generator script (e.g. `scripts/build_docs.py`) that:**
  - (a) updates the existing `基于ChatGPT...优化.docx` (refresh architecture section references from `scrapers/` package), `NEW`, etc.;
  - (b) generates new `项目架构与技术方案.docx` with: 封面 + 目录, 项目概述, 目录树, Factory-pattern 设计说明, 类/解析器/多进程流程图, 数据格式, 运行指南, DOCX-QA.
- [ ] **Step 3: Render both to PNG/PDF and QA visually** — iterate until no overflow/widows/wrong headings; fix then re-render.
- [ ] **Step 4: Commit both `.docx` + generator script.**

```bash
git add -A
git commit -m "docs(docx): update architecture docx and add 项目架构与技术方案.docx"
```

---

### Task 11: Full verification & final review

- [ ] **Step 1: Run whole suite.**

```bash
pip install -q -r requirements.txt pytest python-docx
pytest tests/ -v
```

All pass.

- [ ] **Step 2: Import smoke checks.**

```bash
python -c "from scrapers import create_scraper; print([create_scraper(s) for s in ('hospital','medicine','qa')])"
python run.py --help
```

- [ ] **Step 3: `git status` clean of unexpected deletions; `git log` shows planned commits.** Request a code review of the `scrapers/` package before merging.

---

## Self-Review

- Spec §3 (package layout) → Tasks 2–6. §3.4 factory registry → Task 5. Spec §4 (libs, delete duplicate, correct_name) → Tasks 1, 7, 8. Spec §5 config.py → Task 1. Spec §7 docs → Task 9. Spec §9 docx → Task 10. Tests/verification → Tasks 1–6, 11.
- Placeholder scan: all code steps contain real code; parser ports reference the source `.py` files whose logic they carry over (that logic already exists and is not rewritten from memory).
- Type consistency: every scraper `build_tasks()` yields `(key, url)` pairs; `_worker` consumes `(key, url)`; factory `create(site, **kw)`; `parser.parse(soup, fetch=, logger=) -> dict` consistently referenced.

(A full correctness pass here involves selecting `python-docx` in the docx skill and parity-checking with actual fixture content — this plan assumes that will be verified during execution in Task 10.)