import pytest

import config
from run import build_parser


def test_parser_accepts_valid_sites():
    for site in ('hospital', 'medicine', 'qa'):
        args = build_parser().parse_args([site])
        assert args.site == site


def test_parser_defaults():
    args = build_parser().parse_args(['medicine'])
    assert args.processes == config.DEFAULT_NUM_PROCESSES
    assert args.count is None


def test_parser_rejects_unknown_site():
    with pytest.raises(SystemExit):
        build_parser().parse_args(['nope'])


def test_site_names_constant():
    assert set(config.SITE_NAMES) == {'hospital', 'medicine', 'qa'}