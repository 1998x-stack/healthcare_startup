import pytest

import config
from scrapers.base import BaseScraper


class DummyScraper(BaseScraper):
    site = 'hospital'

    def build_tasks(self):
        return [('k1', 'http://example.com/1'), ('k2', 'http://example.com/2')]


def test_base_is_abstract():
    with pytest.raises(TypeError):
        BaseScraper()


def test_subclass_build_tasks():
    s = DummyScraper()
    assert list(s.build_tasks()) == [('k1', 'http://example.com/1'), ('k2', 'http://example.com/2')]


def test_aggregate_name_derived_from_site():
    assert DummyScraper().aggregate_name() == 'hospital.json'


def test_defaults_from_config():
    s = DummyScraper()
    assert s.num_processes == config.DEFAULT_NUM_PROCESSES
    assert s.save_folder == config.SAVE_FOLDERS['hospital']
    assert s.site == 'hospital'


def test_override_site_and_save_folder(tmp_path):
    s = DummyScraper(site='medicine', save_folder=str(tmp_path), num_processes=2)
    assert s.site == 'medicine'
    assert s.save_folder == str(tmp_path)
    assert s.num_processes == 2