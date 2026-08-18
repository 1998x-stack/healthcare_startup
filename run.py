import argparse

import config
from scrapers import create_scraper


def build_parser():
    ap = argparse.ArgumentParser(prog='run')
    ap.add_argument('site', choices=config.SITE_NAMES,
                    help='which scraper to run: hospital | medicine | qa')
    ap.add_argument('--processes', type=int, default=config.DEFAULT_NUM_PROCESSES,
                    help='number of worker processes')
    ap.add_argument('--count', type=int, default=None,
                    help='number of pages (medicine/qa only)')
    return ap


def main(argv=None):
    args = build_parser().parse_args(argv)
    kwargs = {'num_processes': args.processes}
    if args.count is not None and args.site in ('medicine', 'qa'):
        kwargs['count'] = args.count
    scraper = create_scraper(args.site, **kwargs)
    result = scraper.run()
    print(f'[{args.site}] collected {len(result)} records')
    return result


if __name__ == '__main__':
    main()