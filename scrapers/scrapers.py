import json

import config
from scrapers import urls
from scrapers.base import BaseScraper
from scrapers.parsers import PARSER_REGISTRY


class HospitalScraper(BaseScraper):
    site = 'hospital'

    def __init__(self, site='hospital', **kw):
        super().__init__(site=site, **kw)
        self.parser = PARSER_REGISTRY['hospital']()

    def build_tasks(self):
        with open(config.SEED_DATA['beijing_json'], encoding='utf-8') as f:
            beijing = json.load(f)
        for location, hos in beijing.items():
            for hos_url in hos.get('hospital_url', []):
                yield (f'{location}/{hos_url}', hos_url)


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