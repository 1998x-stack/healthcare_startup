"""Offline end-to-end smoke test: drives the full BaseScraper.run() pipeline
(JoinableQueue multiprocessing + factory + parser + injected fake fetch) with
no network. Verifies the `_thread.lock` pickling fix by actually spawning
worker processes on the current platform's default start method.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tests.fixture_fetch import fake_fetch  # noqa: E402
from scrapers import create_scraper  # noqa: E402

OUT = './data/smoke_out'


def main():
    scraper = create_scraper('medicine', count=2, num_processes=2,
                             fetch=fake_fetch, save_folder=OUT)
    result = scraper.run()
    assert len(result) == 2, f'expected 2 records, got {len(result)}'
    for url, data in result.items():
        assert data['药品名称'] in ('测试药片一', '测试药片二'), data
    agg_path = os.path.join(OUT, 'medicine.json')
    with open(agg_path, encoding='utf-8') as f:
        saved = json.load(f)
    assert len(saved) == 2
    print('SMOKE OK — multiprocessing pipeline worked, aggregate at', agg_path)
    print('keys:', sorted(result))


if __name__ == '__main__':
    main()