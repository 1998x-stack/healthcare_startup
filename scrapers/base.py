import abc
import os
from multiprocessing import JoinableQueue, Process

import config
from libs.log import Log
from libs import utils


def _worker(task_queue, result_queue, parser_name, fetch, logger):
    """Module-level worker for multiprocessing. Only serializable args.

    The parser is resolved by name from the registry inside the worker so the
    parser class objects never need to be pickled.
    """
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
    """Abstract scraper owning the shared pipeline.

    Subclasses set ``site`` and implement ``build_tasks``; field extraction is
    delegated to the parser bound via the factory.
    """

    site = 'base'

    def __init__(self, site=None, save_folder=None, num_processes=None,
                 fetch=None, logger=None):
        self.site = site or self.site
        self.save_folder = save_folder or config.SAVE_FOLDERS.get(self.site, config.SAVE_ROOT)
        self.num_processes = num_processes or config.DEFAULT_NUM_PROCESSES
        self.fetch = fetch or utils.get_soup
        self.logger = logger or Log(self.site)

    @abc.abstractmethod
    def build_tasks(self):
        """Yield (key, url) tuples describing the pages to crawl."""

    def aggregate_name(self):
        return f'{self.site}.json'

    def run(self):
        task_queue = JoinableQueue()
        result_queue = JoinableQueue()

        for task in self.build_tasks():
            task_queue.put(task)
        for _ in range(self.num_processes):
            task_queue.put(None)

        processes = []
        for _ in range(self.num_processes):
            p = Process(target=_worker,
                        args=(task_queue, result_queue, self.site, self.fetch, self.logger))
            p.daemon = True
            p.start()
            processes.append(p)

        task_queue.join()

        aggregate = {}
        while not result_queue.empty():
            key, data = result_queue.get()
            aggregate[key] = data

        for p in processes:
            p.terminate()
            p.join()

        self.save_aggregate(aggregate)
        return aggregate

    def save_aggregate(self, aggregate):
        utils.save_js(aggregate, logger=self.logger, save_folder=self.save_folder,
                      file_name=self.aggregate_name())