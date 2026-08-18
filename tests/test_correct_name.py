import os

from libs.tools.correct_name import recover, run


def test_recover_latin1_mojibake():
    # 'éª¨' is the UTF-8 bytes of 骨 read as Latin-1 -> recover to 骨
    bad = '骨'.encode('utf-8').decode('latin-1')
    assert recover(bad) == '骨'


def test_recover_returns_none_for_clean_name():
    assert recover('正常名称') is None
    assert recover('plain.txt') is None


def test_recover_returns_none_for_unrecoverable():
    assert recover('»±¾Íâ¿Æ') is None


def test_dry_run_does_not_rename(tmp_path):
    bad = '骨'.encode('utf-8').decode('latin-1')
    p = tmp_path / f'{bad}.json'
    p.write_text('{}', encoding='utf-8')
    applied, skipped = run(str(tmp_path), dry_run=True)
    assert applied and p.exists()  # dry-run renamed nothing but reported
    assert not os.path.exists(tmp_path / '骨.json')


def test_run_renames_recoverable(tmp_path):
    bad = '骨'.encode('utf-8').decode('latin-1')
    p = tmp_path / f'{bad}.json'
    p.write_text('{}', encoding='utf-8')
    applied, skipped = run(str(tmp_path), dry_run=False)
    assert os.path.exists(tmp_path / '骨.json')
    assert not p.exists()