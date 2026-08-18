import os
import tempfile

from libs.utils import save_csv, save_js, silent_logger


def test_save_js_with_no_logger_creates_file():
    with tempfile.TemporaryDirectory() as d:
        path = os.path.join(d, 'sub', 'x.json')
        save_js({'a': 1}, save_folder=os.path.dirname(path), file_name='x.json')
        assert os.path.exists(path)


def test_save_js_default_folder_and_silent_logger():
    with tempfile.TemporaryDirectory() as d:
        save_js({'b': 2}, save_folder=d, file_name='y.json', logger=silent_logger())
        assert os.path.exists(os.path.join(d, 'y.json'))


def test_save_js_strips_illegal_filename_chars():
    with tempfile.TemporaryDirectory() as d:
        save_js({}, save_folder=d, file_name='a/b:c.json')
        # '\\', '/', ':', '*', '?', '"', '<', '>', '|' removed
        joined = [f for f in os.listdir(d)]
        assert any('b:c.json' not in f and f.endswith('.json') for f in joined)


def test_save_csv_without_logger():
    import libs.utils as u
    with tempfile.TemporaryDirectory() as d:
        u.save_csv([['h1', 'h2'], [1, 2]], save_folder=d, file_name='data.csv')
        assert os.path.exists(os.path.join(d, 'data.csv'))