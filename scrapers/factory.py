from scrapers.scrapers import HospitalScraper, MedicineScraper, QAScraper

SCRAPER_REGISTRY = {
    'hospital': HospitalScraper,
    'medicine': MedicineScraper,
    'qa': QAScraper,
}


class ScraperFactory:
    """Returns a concrete scraper bound to its site-specific parser.

    Each site entry maps to a `(scraper_cls, parser_cls)` pair selected by the
    concrete scraper itself; adding a new site means registering a new parser
    and scraper class in ``SCRAPER_REGISTRY``.
    """

    def create(self, site, **kwargs):
        if site not in SCRAPER_REGISTRY:
            raise ValueError(f'Unknown site: {site}')
        return SCRAPER_REGISTRY[site](site=site, **kwargs)


create_scraper = ScraperFactory().create