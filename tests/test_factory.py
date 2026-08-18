import pytest

from scrapers import ScraperFactory, create_scraper


def test_factory_returns_hospital():
    s = create_scraper('hospital')
    assert s.__class__.__name__ == 'HospitalScraper'
    assert s.parser.name == 'hospital'


def test_factory_returns_medicine_and_qa():
    assert create_scraper('medicine').parser.name == 'medicine'
    assert create_scraper('qa').parser.name == 'qa'


def test_factory_unknown_raises():
    with pytest.raises(ValueError):
        create_scraper('nope')


def test_factory_create_method_and_module_agree():
    assert ScraperFactory().create('medicine').site == create_scraper('medicine').site == 'medicine'